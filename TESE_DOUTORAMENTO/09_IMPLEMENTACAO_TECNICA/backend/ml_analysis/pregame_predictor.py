"""
Pre-Game Performance Drop Predictor for Football Substitution Guidance
======================================================================

Thesis objective: Predict the probability of a player experiencing a physical
performance drop during a match, using only pre-game data, to guide
substitution decisions.

Target variable:
    target = 1 if in-game performance drop detected:
        - HSR/min < 85% of individual baseline (rolling 4-game avg) OR
        - sprint_rate z-score < -1 (individual rolling window) OR
        - distance drop > 20% between 1st half and last 20 min proxy
    target = 0 otherwise

Features (all computed BEFORE the game):
    1. Cumulative loads: 3/7/14/28-day EMA of sRPE, HSR, distance, acc/dec
    2. ACWR = EMA7 / EMA28 for key variables
    3. Monotony, strain, slope, deltas
    4. Wellness: 3d/7d averages, delta vs 28d baseline, individual z-scores
    5. Exposure: 7d/14d minutes, days since last game, consecutive games
    6. Tactical (last 2 games): normalized per athlete

Validation: Temporal split (train games 1-N, test games N+1-M) with
            walk-forward option.

Model: XGBoost binary classifier with SHAP explainability.

Author: Doctoral research — Predição de Substituições no Futebol
"""

import logging
import warnings
import pickle
import os
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    roc_auc_score, precision_recall_curve, auc,
    classification_report, balanced_accuracy_score,
    precision_score, recall_score, f1_score, confusion_matrix
)

try:
    import xgboost as xgb
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False

warnings.filterwarnings("ignore", category=UserWarning)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MODEL_DIR = os.path.join(os.path.dirname(__file__), "saved_models")
MODEL_PATH = os.path.join(MODEL_DIR, "pregame_xgb_model.pkl")

# EMA spans (days)
EMA_SPANS = [3, 7, 14, 28]

# Target thresholds
HSR_BASELINE_PCT = 0.85       # HSR/min < 85% of baseline → drop
SPRINT_ZSCORE_THRESH = -1.0   # sprint z-score < -1 → drop
DISTANCE_DROP_PCT = 0.20      # >20% distance drop 1H vs last period → drop
BASELINE_GAMES = 4            # rolling window for individual baseline


# ===================================================================
# DATA LOADING — pulls raw data from the database into DataFrames
# ===================================================================
class DataLoader:
    """Loads and structures all required data from the PostgreSQL database."""

    def __init__(self, db):
        self.db = db

    def load_sessions(self) -> pd.DataFrame:
        """Load all sessions with type and date."""
        rows = self.db.query_to_dict(
            "SELECT id, data, tipo, adversario, jornada, duracao_min, resultado "
            "FROM sessoes ORDER BY data"
        )
        df = pd.DataFrame(rows)
        if not df.empty:
            df["data"] = pd.to_datetime(df["data"])
            df["is_game"] = df["tipo"].str.lower() == "jogo"
        return df

    @staticmethod
    def _to_numeric(df: pd.DataFrame) -> pd.DataFrame:
        """Convert Decimal columns to float to avoid pandas type errors."""
        from decimal import Decimal
        for col in df.columns:
            if df[col].dtype == object and len(df) > 0:
                sample = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
                if isinstance(sample, Decimal):
                    df[col] = df[col].apply(lambda x: float(x) if x is not None else None).astype(float)
        return df

    def load_gps(self) -> pd.DataFrame:
        """Load all GPS records joined with session date."""
        rows = self.db.query_to_dict("""
            SELECT g.atleta_id, g.sessao_id, s.data,
                   LOWER(s.tipo) as tipo,
                   g.distancia_total, g.velocidade_max,
                   g.sprints, g.aceleracoes, g.desaceleracoes,
                   g.player_load,
                   g.effs_19_8_kmh as hsr_efforts,
                   g.dist_19_8_kmh as hsr_distance,
                   g.effs_25_2_kmh as sprint_efforts,
                   s.duracao_min
            FROM dados_gps g
            JOIN sessoes s ON s.id = g.sessao_id
            ORDER BY s.data, g.atleta_id
        """)
        df = pd.DataFrame(rows)
        if not df.empty:
            df = self._to_numeric(df)
            df["data"] = pd.to_datetime(df["data"])
            # Compute per-minute rates
            dur = df["duracao_min"].replace(0, np.nan).fillna(90)
            df["dist_per_min"] = df["distancia_total"] / dur
            df["hsr_per_min"] = df["hsr_distance"].fillna(0) / dur
            df["sprint_per_min"] = df["sprint_efforts"].fillna(0) / dur
        return df

    def load_pse(self) -> pd.DataFrame:
        """Load RPE / internal load data."""
        rows = self.db.query_to_dict("""
            SELECT p.atleta_id, p.sessao_id, s.data,
                   p.pse as rpe, p.duracao_min, p.carga_total as srpe,
                   p.qualidade_sono, p.fadiga, p.dor_muscular, p.stress
            FROM dados_pse p
            JOIN sessoes s ON s.id = p.sessao_id
            ORDER BY s.data, p.atleta_id
        """)
        df = pd.DataFrame(rows)
        if not df.empty:
            df = self._to_numeric(df)
            df["data"] = pd.to_datetime(df["data"])
            # Ensure sRPE exists
            if "srpe" not in df.columns or df["srpe"].isna().all():
                df["srpe"] = df["rpe"].fillna(5) * df["duracao_min"].fillna(90)
        return df

    def load_wellness(self) -> pd.DataFrame:
        """Load wellness questionnaire data."""
        rows = self.db.query_to_dict("""
            SELECT atleta_id, data,
                   wellness_score, fatigue_level, muscle_soreness,
                   sleep_quality, sleep_hours, stress_level, mood,
                   readiness_score
            FROM dados_wellness
            ORDER BY data, atleta_id
        """)
        df = pd.DataFrame(rows)
        if not df.empty:
            df = self._to_numeric(df)
            df["data"] = pd.to_datetime(df["data"])
        return df

    def load_metricas_carga(self) -> pd.DataFrame:
        """Load pre-computed weekly load metrics."""
        rows = self.db.query_to_dict("""
            SELECT atleta_id, semana_inicio, semana_fim,
                   carga_total_semanal, monotonia, tensao, acwr,
                   carga_aguda, carga_cronica, dias_treino,
                   distancia_total_media, velocidade_max_media,
                   aceleracoes_media, high_speed_distance
            FROM metricas_carga
            ORDER BY semana_inicio, atleta_id
        """)
        df = pd.DataFrame(rows)
        if not df.empty:
            df = self._to_numeric(df)
            df["semana_inicio"] = pd.to_datetime(df["semana_inicio"])
            df["semana_fim"] = pd.to_datetime(df["semana_fim"])
        return df

    def load_athletes(self) -> pd.DataFrame:
        rows = self.db.query_to_dict(
            "SELECT id, nome_completo, posicao, numero_camisola, ativo FROM atletas"
        )
        return pd.DataFrame(rows)


# ===================================================================
# TARGET VARIABLE — defines when a player had a performance drop
# ===================================================================
class TargetBuilder:
    """
    Builds the binary target for each (athlete, game) pair.

    A player is labelled target=1 (performance drop) if ANY of:
        Rule A: HSR/min in this game < 85% of their rolling baseline
        Rule B: sprint_per_min z-score < -1 (rolling 4-game window)
        Rule C: distance_per_min drop > 20% vs their rolling baseline

    The baseline is the mean of the player's previous BASELINE_GAMES games
    (strict look-back — no leakage).
    """

    @staticmethod
    def build(gps: pd.DataFrame, sessions: pd.DataFrame) -> pd.DataFrame:
        """
        Returns DataFrame with columns:
            atleta_id, sessao_id, data, target, rule_a, rule_b, rule_c,
            hsr_per_min, sprint_per_min, dist_per_min,
            baseline_hsr, baseline_sprint_mean, baseline_sprint_std,
            baseline_dist
        """
        # Filter to game sessions only
        game_ids = set(sessions.loc[sessions["is_game"], "id"])
        game_gps = gps[gps["sessao_id"].isin(game_ids)].copy()

        if game_gps.empty:
            return pd.DataFrame()

        game_gps = game_gps.sort_values(["atleta_id", "data"])

        results = []
        for aid, grp in game_gps.groupby("atleta_id"):
            grp = grp.sort_values("data").reset_index(drop=True)
            for i, row in grp.iterrows():
                prev = grp.iloc[max(0, i - BASELINE_GAMES):i]
                if len(prev) < 1:
                    # First game — no baseline, skip or label 0
                    results.append({
                        "atleta_id": aid,
                        "sessao_id": row["sessao_id"],
                        "data": row["data"],
                        "target": 0,
                        "rule_a": False, "rule_b": False, "rule_c": False,
                        "hsr_per_min": row["hsr_per_min"],
                        "sprint_per_min": row["sprint_per_min"],
                        "dist_per_min": row["dist_per_min"],
                        "baseline_hsr": np.nan,
                        "baseline_sprint_mean": np.nan,
                        "baseline_sprint_std": np.nan,
                        "baseline_dist": np.nan,
                        "has_baseline": False,
                    })
                    continue

                bl_hsr = prev["hsr_per_min"].mean()
                bl_sprint_mean = prev["sprint_per_min"].mean()
                bl_sprint_std = prev["sprint_per_min"].std()
                bl_dist = prev["dist_per_min"].mean()

                # Rule A: HSR/min < 85% of baseline
                rule_a = (row["hsr_per_min"] < HSR_BASELINE_PCT * bl_hsr) if bl_hsr > 0 else False

                # Rule B: sprint z-score < -1
                if bl_sprint_std and bl_sprint_std > 0:
                    z_sprint = (row["sprint_per_min"] - bl_sprint_mean) / bl_sprint_std
                    rule_b = z_sprint < SPRINT_ZSCORE_THRESH
                else:
                    rule_b = False

                # Rule C: distance drop > 20% vs baseline
                rule_c = (row["dist_per_min"] < (1 - DISTANCE_DROP_PCT) * bl_dist) if bl_dist > 0 else False

                target = int(rule_a or rule_b or rule_c)

                results.append({
                    "atleta_id": aid,
                    "sessao_id": row["sessao_id"],
                    "data": row["data"],
                    "target": target,
                    "rule_a": bool(rule_a),
                    "rule_b": bool(rule_b),
                    "rule_c": bool(rule_c),
                    "hsr_per_min": row["hsr_per_min"],
                    "sprint_per_min": row["sprint_per_min"],
                    "dist_per_min": row["dist_per_min"],
                    "baseline_hsr": bl_hsr,
                    "baseline_sprint_mean": bl_sprint_mean,
                    "baseline_sprint_std": bl_sprint_std,
                    "baseline_dist": bl_dist,
                    "has_baseline": True,
                })

        return pd.DataFrame(results)


# ===================================================================
# FEATURE ENGINEERING — all features computed BEFORE the game
# ===================================================================
class FeatureEngineer:
    """
    Builds pre-game features for each (athlete, game_date) pair.

    All features use only data strictly before the game date (no leakage).
    """

    def __init__(self, gps: pd.DataFrame, pse: pd.DataFrame,
                 wellness: pd.DataFrame, sessions: pd.DataFrame):
        self.gps = gps.copy()
        self.pse = pse.copy()
        self.wellness = wellness.copy()
        self.sessions = sessions.copy()

    def build_features(self, targets: pd.DataFrame) -> pd.DataFrame:
        """Build feature matrix aligned with target rows."""
        features_list = []

        for _, row in targets.iterrows():
            aid = row["atleta_id"]
            game_date = row["data"]
            feats = {"atleta_id": aid, "sessao_id": row["sessao_id"], "data": game_date}

            # --- Cumulative Load Features ---
            feats.update(self._load_features(aid, game_date))

            # --- Wellness Features ---
            feats.update(self._wellness_features(aid, game_date))

            # --- Exposure Features ---
            feats.update(self._exposure_features(aid, game_date))

            # --- GPS Trend Features ---
            feats.update(self._gps_trend_features(aid, game_date))

            features_list.append(feats)

        df = pd.DataFrame(features_list)
        return df

    def _ema(self, series: pd.Series, span: int) -> float:
        """Compute EMA of a series with given span."""
        if series.empty:
            return 0.0
        return float(series.ewm(span=span, min_periods=1).mean().iloc[-1])

    def _load_features(self, aid: int, game_date) -> Dict:
        """Cumulative load features from PSE + GPS data before game_date."""
        feats = {}

        # PSE-based loads
        pse_before = self.pse[
            (self.pse["atleta_id"] == aid) & (self.pse["data"] < game_date)
        ].sort_values("data")

        srpe = pse_before["srpe"].fillna(0)
        rpe = pse_before["rpe"].fillna(0)

        for span in EMA_SPANS:
            feats[f"srpe_ema_{span}d"] = self._ema(srpe, span)
            feats[f"rpe_ema_{span}d"] = self._ema(rpe, span)

        # ACWR for sRPE
        feats["srpe_acwr"] = (
            feats["srpe_ema_7d"] / feats["srpe_ema_28d"]
            if feats["srpe_ema_28d"] > 0 else 1.0
        )

        # Monotony & Strain (7-day window)
        last_7d = pse_before[pse_before["data"] >= (game_date - pd.Timedelta(days=7))]
        daily_load = last_7d.groupby(last_7d["data"].dt.date)["srpe"].sum()
        if len(daily_load) >= 2:
            feats["monotony_7d"] = float(daily_load.mean() / daily_load.std()) if daily_load.std() > 0 else 0.0
            feats["strain_7d"] = float(daily_load.sum() * feats["monotony_7d"])
        else:
            feats["monotony_7d"] = 0.0
            feats["strain_7d"] = 0.0

        # Slope (7d trend) — linear regression slope of daily sRPE
        last_14d = pse_before[pse_before["data"] >= (game_date - pd.Timedelta(days=14))]
        daily_14d = last_14d.groupby(last_14d["data"].dt.date)["srpe"].sum().reset_index()
        if len(daily_14d) >= 3:
            x = np.arange(len(daily_14d))
            y = daily_14d["srpe"].values
            slope = np.polyfit(x, y, 1)[0]
            feats["srpe_slope_14d"] = float(slope)
        else:
            feats["srpe_slope_14d"] = 0.0

        # Delta: EMA7 - EMA28
        feats["srpe_delta_7_28"] = feats["srpe_ema_7d"] - feats["srpe_ema_28d"]

        # GPS-based loads
        gps_before = self.gps[
            (self.gps["atleta_id"] == aid) & (self.gps["data"] < game_date)
        ].sort_values("data")

        dist = gps_before["distancia_total"].fillna(0)
        hsr = gps_before["hsr_distance"].fillna(0)
        acc = gps_before["aceleracoes"].fillna(0)
        dec = gps_before["desaceleracoes"].fillna(0)

        for span in EMA_SPANS:
            feats[f"dist_ema_{span}d"] = self._ema(dist, span)
            feats[f"hsr_ema_{span}d"] = self._ema(hsr, span)
            feats[f"acc_ema_{span}d"] = self._ema(acc, span)
            feats[f"dec_ema_{span}d"] = self._ema(dec, span)

        # ACWR for distance and HSR
        feats["dist_acwr"] = (
            feats["dist_ema_7d"] / feats["dist_ema_28d"]
            if feats["dist_ema_28d"] > 0 else 1.0
        )
        feats["hsr_acwr"] = (
            feats["hsr_ema_7d"] / feats["hsr_ema_28d"]
            if feats["hsr_ema_28d"] > 0 else 1.0
        )

        # Deltas
        feats["dist_delta_7_28"] = feats["dist_ema_7d"] - feats["dist_ema_28d"]
        feats["hsr_delta_7_28"] = feats["hsr_ema_7d"] - feats["hsr_ema_28d"]

        return feats

    def _wellness_features(self, aid: int, game_date) -> Dict:
        """Wellness features from questionnaire data before game_date."""
        feats = {}

        w = self.wellness[
            (self.wellness["atleta_id"] == aid) & (self.wellness["data"] < game_date)
        ].sort_values("data")

        ws = w["wellness_score"].fillna(0)
        fatigue = w["fatigue_level"].fillna(0)
        soreness = w["muscle_soreness"].fillna(0)
        sleep = w["sleep_quality"].fillna(0)
        stress = w["stress_level"].fillna(0)

        # 3d and 7d averages
        last_3d = w[w["data"] >= (game_date - pd.Timedelta(days=3))]
        last_7d = w[w["data"] >= (game_date - pd.Timedelta(days=7))]
        last_28d = w[w["data"] >= (game_date - pd.Timedelta(days=28))]

        feats["wellness_avg_3d"] = float(last_3d["wellness_score"].mean()) if not last_3d.empty else 0.0
        feats["wellness_avg_7d"] = float(last_7d["wellness_score"].mean()) if not last_7d.empty else 0.0
        feats["wellness_avg_28d"] = float(last_28d["wellness_score"].mean()) if not last_28d.empty else 0.0

        # Delta wellness: 3d vs 28d baseline
        feats["wellness_delta_3_28"] = feats["wellness_avg_3d"] - feats["wellness_avg_28d"]

        # Individual z-score (28d window)
        if not last_28d.empty and last_28d["wellness_score"].std() > 0:
            recent_val = last_3d["wellness_score"].mean() if not last_3d.empty else last_28d["wellness_score"].iloc[-1]
            feats["wellness_zscore_28d"] = float(
                (recent_val - last_28d["wellness_score"].mean()) / last_28d["wellness_score"].std()
            )
        else:
            feats["wellness_zscore_28d"] = 0.0

        # Component averages (3d)
        feats["fatigue_avg_3d"] = float(last_3d["fatigue_level"].mean()) if not last_3d.empty else 0.0
        feats["soreness_avg_3d"] = float(last_3d["muscle_soreness"].mean()) if not last_3d.empty else 0.0
        feats["sleep_avg_3d"] = float(last_3d["sleep_quality"].mean()) if not last_3d.empty else 0.0
        feats["stress_avg_3d"] = float(last_3d["stress_level"].mean()) if not last_3d.empty else 0.0

        # Component averages (7d)
        feats["fatigue_avg_7d"] = float(last_7d["fatigue_level"].mean()) if not last_7d.empty else 0.0
        feats["soreness_avg_7d"] = float(last_7d["muscle_soreness"].mean()) if not last_7d.empty else 0.0
        feats["sleep_avg_7d"] = float(last_7d["sleep_quality"].mean()) if not last_7d.empty else 0.0
        feats["stress_avg_7d"] = float(last_7d["stress_level"].mean()) if not last_7d.empty else 0.0

        # Readiness (latest)
        if not w.empty and "readiness_score" in w.columns:
            feats["readiness_latest"] = float(w["readiness_score"].iloc[-1]) if pd.notna(w["readiness_score"].iloc[-1]) else 0.0
        else:
            feats["readiness_latest"] = 0.0

        return feats

    def _exposure_features(self, aid: int, game_date) -> Dict:
        """Exposure / match load features."""
        feats = {}

        # Minutes played in last 7d and 14d (from PSE duration)
        pse_before = self.pse[
            (self.pse["atleta_id"] == aid) & (self.pse["data"] < game_date)
        ]
        last_7d = pse_before[pse_before["data"] >= (game_date - pd.Timedelta(days=7))]
        last_14d = pse_before[pse_before["data"] >= (game_date - pd.Timedelta(days=14))]

        feats["minutes_7d"] = float(last_7d["duracao_min"].sum()) if not last_7d.empty else 0.0
        feats["minutes_14d"] = float(last_14d["duracao_min"].sum()) if not last_14d.empty else 0.0

        # Days since last game
        game_sessions = self.sessions[self.sessions["is_game"]].sort_values("data")
        prev_games = game_sessions[
            (game_sessions["data"] < game_date)
        ]
        if not prev_games.empty:
            last_game_date = prev_games["data"].iloc[-1]
            feats["days_since_last_game"] = (game_date - last_game_date).days
        else:
            feats["days_since_last_game"] = 30  # default if no previous game

        # Consecutive games in last 14 days
        recent_games = game_sessions[
            (game_sessions["data"] >= (game_date - pd.Timedelta(days=14))) &
            (game_sessions["data"] < game_date)
        ]
        feats["consecutive_games_14d"] = len(recent_games)

        # Sessions count in last 7d
        all_sessions_before = self.gps[
            (self.gps["atleta_id"] == aid) &
            (self.gps["data"] >= (game_date - pd.Timedelta(days=7))) &
            (self.gps["data"] < game_date)
        ]
        feats["sessions_7d"] = int(all_sessions_before["sessao_id"].nunique())

        return feats

    def _gps_trend_features(self, aid: int, game_date) -> Dict:
        """GPS performance trends from recent sessions."""
        feats = {}

        gps_before = self.gps[
            (self.gps["atleta_id"] == aid) & (self.gps["data"] < game_date)
        ].sort_values("data")

        # Last 4 sessions averages
        last_4 = gps_before.tail(4)
        feats["dist_avg_last4"] = float(last_4["distancia_total"].mean()) if not last_4.empty else 0.0
        feats["hsr_avg_last4"] = float(last_4["hsr_distance"].fillna(0).mean()) if not last_4.empty else 0.0
        feats["sprint_avg_last4"] = float(last_4["sprint_efforts"].fillna(0).mean()) if not last_4.empty else 0.0
        feats["acc_avg_last4"] = float(last_4["aceleracoes"].fillna(0).mean()) if not last_4.empty else 0.0
        feats["vmax_avg_last4"] = float(last_4["velocidade_max"].fillna(0).mean()) if not last_4.empty else 0.0

        # Trend: last 2 vs previous 2
        if len(gps_before) >= 4:
            recent_2 = gps_before.tail(2)
            prev_2 = gps_before.iloc[-4:-2]
            r2_dist = recent_2["distancia_total"].mean()
            p2_dist = prev_2["distancia_total"].mean()
            feats["dist_trend_ratio"] = float(r2_dist / p2_dist) if p2_dist > 0 else 1.0

            r2_hsr = recent_2["hsr_distance"].fillna(0).mean()
            p2_hsr = prev_2["hsr_distance"].fillna(0).mean()
            feats["hsr_trend_ratio"] = float(r2_hsr / p2_hsr) if p2_hsr > 0 else 1.0
        else:
            feats["dist_trend_ratio"] = 1.0
            feats["hsr_trend_ratio"] = 1.0

        return feats


# ===================================================================
# MODEL — XGBoost training, validation, prediction
# ===================================================================
class PreGamePredictor:
    """
    XGBoost binary classifier for pre-game performance drop prediction.
    Includes temporal validation, SHAP explainability, and model persistence.
    """

    # Feature columns (excluding identifiers)
    ID_COLS = ["atleta_id", "sessao_id", "data"]

    def __init__(self):
        self.model = None
        self.feature_names = None
        self.shap_explainer = None
        self.training_report = None
        self.is_trained = False

    def get_feature_cols(self, df: pd.DataFrame) -> List[str]:
        """Return feature column names (everything except ID columns and target)."""
        return [c for c in df.columns if c not in self.ID_COLS + ["target"]]

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------
    def train(self, features: pd.DataFrame, targets: pd.DataFrame,
              train_game_ids: List[int] = None,
              test_game_ids: List[int] = None,
              walk_forward: bool = False) -> Dict[str, Any]:
        """
        Train the XGBoost model with temporal validation.

        Parameters
        ----------
        features : DataFrame with pre-game features
        targets : DataFrame with target labels
        train_game_ids : list of session IDs for training (optional)
        test_game_ids : list of session IDs for testing (optional)
        walk_forward : if True, use expanding walk-forward validation

        Returns
        -------
        dict with training report, metrics, feature importances
        """
        if not HAS_XGB:
            raise RuntimeError("xgboost not installed")

        # Merge features with targets
        df = features.merge(
            targets[["atleta_id", "sessao_id", "target"]],
            on=["atleta_id", "sessao_id"],
            how="inner"
        )

        # Drop rows with NaN target
        df = df.dropna(subset=["target"])
        df["target"] = df["target"].astype(int)

        feature_cols = self.get_feature_cols(df)
        self.feature_names = feature_cols

        # Fill NaN features with 0
        df[feature_cols] = df[feature_cols].fillna(0)

        # --- Temporal split ---
        if train_game_ids is not None and test_game_ids is not None:
            train_mask = df["sessao_id"].isin(train_game_ids)
            test_mask = df["sessao_id"].isin(test_game_ids)
        else:
            # Default: sort by date, first 70% train, rest test
            df = df.sort_values("data")
            unique_games = df["sessao_id"].unique()
            split_idx = int(len(unique_games) * 0.7)
            train_ids = unique_games[:split_idx]
            test_ids = unique_games[split_idx:]
            train_mask = df["sessao_id"].isin(train_ids)
            test_mask = df["sessao_id"].isin(test_ids)

        X_train = df.loc[train_mask, feature_cols].values
        y_train = df.loc[train_mask, "target"].values
        X_test = df.loc[test_mask, feature_cols].values
        y_test = df.loc[test_mask, "target"].values

        logger.info(f"Training set: {len(X_train)} samples, {y_train.sum()} positives ({y_train.mean()*100:.1f}%)")
        logger.info(f"Test set: {len(X_test)} samples, {y_test.sum()} positives ({y_test.mean()*100:.1f}%)")

        # Handle class imbalance
        n_pos = max(y_train.sum(), 1)
        n_neg = max(len(y_train) - n_pos, 1)
        scale_pos_weight = n_neg / n_pos

        # XGBoost parameters
        params = {
            "objective": "binary:logistic",
            "eval_metric": "aucpr",
            "max_depth": 4,
            "learning_rate": 0.05,
            "n_estimators": 300,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "min_child_weight": 3,
            "scale_pos_weight": scale_pos_weight,
            "random_state": 42,
            "verbosity": 0,
        }

        # Train with early stopping
        dtrain = xgb.DMatrix(X_train, label=y_train, feature_names=feature_cols)
        dtest = xgb.DMatrix(X_test, label=y_test, feature_names=feature_cols)

        xgb_params = {
            "objective": params["objective"],
            "eval_metric": params["eval_metric"],
            "max_depth": params["max_depth"],
            "learning_rate": params["learning_rate"],
            "subsample": params["subsample"],
            "colsample_bytree": params["colsample_bytree"],
            "min_child_weight": params["min_child_weight"],
            "scale_pos_weight": params["scale_pos_weight"],
            "seed": 42,
            "verbosity": 0,
        }

        evals = [(dtrain, "train"), (dtest, "eval")]
        self.model = xgb.train(
            xgb_params, dtrain,
            num_boost_round=params["n_estimators"],
            evals=evals,
            early_stopping_rounds=30,
            verbose_eval=False,
        )

        # Predictions
        y_prob_train = self.model.predict(dtrain)
        y_prob_test = self.model.predict(dtest)
        y_pred_test = (y_prob_test >= 0.5).astype(int)

        # Metrics
        metrics = self._compute_metrics(y_test, y_prob_test, y_pred_test)
        train_metrics = self._compute_metrics(y_train, y_prob_train, (y_prob_train >= 0.5).astype(int))

        # Feature importance
        importance = self.model.get_score(importance_type="gain")
        sorted_imp = sorted(importance.items(), key=lambda x: x[1], reverse=True)

        # SHAP
        shap_summary = None
        if HAS_SHAP:
            try:
                self.shap_explainer = shap.TreeExplainer(self.model)
                shap_values = self.shap_explainer.shap_values(dtest)
                mean_abs_shap = np.abs(shap_values).mean(axis=0)
                shap_summary = [
                    {"feature": feature_cols[i], "mean_abs_shap": float(mean_abs_shap[i])}
                    for i in np.argsort(-mean_abs_shap)[:15]
                ]
            except Exception as e:
                logger.warning(f"SHAP computation failed: {e}")

        self.is_trained = True

        # Build report
        self.training_report = {
            "params": params,
            "dataset": {
                "total_samples": len(df),
                "train_samples": len(X_train),
                "test_samples": len(X_test),
                "train_positive_rate": float(y_train.mean()),
                "test_positive_rate": float(y_test.mean()),
                "scale_pos_weight": round(scale_pos_weight, 2),
                "n_features": len(feature_cols),
                "n_games_train": int(df.loc[train_mask, "sessao_id"].nunique()),
                "n_games_test": int(df.loc[test_mask, "sessao_id"].nunique()),
            },
            "train_metrics": train_metrics,
            "test_metrics": metrics,
            "feature_importance": [
                {"feature": f, "gain": round(g, 4)} for f, g in sorted_imp[:20]
            ],
            "shap_summary": shap_summary,
            "best_iteration": self.model.best_iteration if hasattr(self.model, "best_iteration") else None,
        }

        # Save model
        self._save_model()

        return self.training_report

    def _compute_metrics(self, y_true, y_prob, y_pred) -> Dict:
        """Compute classification metrics."""
        metrics = {}

        if len(np.unique(y_true)) < 2:
            metrics["warning"] = "Only one class in y_true — metrics may be unreliable"
            metrics["auc_roc"] = 0.0
            metrics["auc_pr"] = 0.0
        else:
            metrics["auc_roc"] = round(float(roc_auc_score(y_true, y_prob)), 4)
            prec_curve, rec_curve, _ = precision_recall_curve(y_true, y_prob)
            metrics["auc_pr"] = round(float(auc(rec_curve, prec_curve)), 4)

        metrics["precision"] = round(float(precision_score(y_true, y_pred, zero_division=0)), 4)
        metrics["recall"] = round(float(recall_score(y_true, y_pred, zero_division=0)), 4)
        metrics["f1"] = round(float(f1_score(y_true, y_pred, zero_division=0)), 4)
        metrics["balanced_accuracy"] = round(float(balanced_accuracy_score(y_true, y_pred)), 4)

        cm = confusion_matrix(y_true, y_pred)
        metrics["confusion_matrix"] = cm.tolist()

        return metrics

    # ------------------------------------------------------------------
    # Prediction for new games
    # ------------------------------------------------------------------
    def predict(self, features: pd.DataFrame) -> pd.DataFrame:
        """
        Predict performance drop probability for upcoming game.

        Parameters
        ----------
        features : DataFrame with pre-game features (same columns as training)

        Returns
        -------
        DataFrame with atleta_id, probability, severity, shap_factors
        """
        if not self.is_trained and not self._load_model():
            raise RuntimeError("Model not trained. Call train() first.")

        feature_cols = self.feature_names
        X = features[feature_cols].fillna(0).values
        dmatrix = xgb.DMatrix(X, feature_names=feature_cols)

        probs = self.model.predict(dmatrix)

        results = features[["atleta_id"]].copy()
        results["probability"] = probs
        results["severity"] = results["probability"].apply(self._severity_label)

        # SHAP explanations
        if self.shap_explainer is not None:
            try:
                shap_values = self.shap_explainer.shap_values(dmatrix)
                shap_factors = []
                for i in range(len(X)):
                    top_idx = np.argsort(-np.abs(shap_values[i]))[:5]
                    factors = [
                        {
                            "feature": feature_cols[j],
                            "shap_value": round(float(shap_values[i][j]), 4),
                            "feature_value": round(float(X[i][j]), 4),
                            "direction": "risk" if shap_values[i][j] > 0 else "protective",
                        }
                        for j in top_idx
                    ]
                    shap_factors.append(factors)
                results["shap_factors"] = shap_factors
            except Exception as e:
                logger.warning(f"SHAP prediction failed: {e}")
                results["shap_factors"] = [[] for _ in range(len(X))]
        else:
            results["shap_factors"] = [[] for _ in range(len(X))]

        return results

    @staticmethod
    def _severity_label(prob: float) -> str:
        if prob >= 0.70:
            return "critical"
        elif prob >= 0.50:
            return "high"
        elif prob >= 0.30:
            return "moderate"
        else:
            return "low"

    # ------------------------------------------------------------------
    # Model persistence
    # ------------------------------------------------------------------
    def _save_model(self):
        os.makedirs(MODEL_DIR, exist_ok=True)
        state = {
            "model": self.model,
            "feature_names": self.feature_names,
            "training_report": self.training_report,
        }
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(state, f)
        logger.info(f"Model saved to {MODEL_PATH}")

    def _load_model(self) -> bool:
        if not os.path.exists(MODEL_PATH):
            return False
        try:
            with open(MODEL_PATH, "rb") as f:
                state = pickle.load(f)
            self.model = state["model"]
            self.feature_names = state["feature_names"]
            self.training_report = state.get("training_report")
            self.is_trained = True

            if HAS_SHAP:
                try:
                    self.shap_explainer = shap.TreeExplainer(self.model)
                except:
                    pass

            logger.info("Model loaded from disk")
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False


# ===================================================================
# PIPELINE — orchestrates the full train/predict workflow
# ===================================================================
class PreGamePipeline:
    """
    End-to-end pipeline: load data → build target → engineer features
    → train model → evaluate → predict.
    """

    def __init__(self, db):
        self.db = db
        self.loader = DataLoader(db)
        self.predictor = PreGamePredictor()

        # Cached data
        self.sessions = None
        self.gps = None
        self.pse = None
        self.wellness = None
        self.athletes = None
        self.targets = None
        self.features = None

    def load_data(self):
        """Load all data from database."""
        logger.info("Loading data from database...")
        self.sessions = self.loader.load_sessions()
        self.gps = self.loader.load_gps()
        self.pse = self.loader.load_pse()
        self.wellness = self.loader.load_wellness()
        self.athletes = self.loader.load_athletes()

        logger.info(
            f"Loaded: {len(self.sessions)} sessions, "
            f"{len(self.gps)} GPS records, {len(self.pse)} PSE records, "
            f"{len(self.wellness)} wellness records, {len(self.athletes)} athletes"
        )

    def build_target(self) -> pd.DataFrame:
        """Build target variable for all (athlete, game) pairs."""
        logger.info("Building target variable...")
        self.targets = TargetBuilder.build(self.gps, self.sessions)

        if self.targets.empty:
            logger.warning("No game data found — cannot build targets")
            return self.targets

        n_pos = self.targets["target"].sum()
        n_total = len(self.targets)
        logger.info(
            f"Target built: {n_total} athlete-game pairs, "
            f"{n_pos} drops ({n_pos/n_total*100:.1f}%)"
        )

        # Log rule breakdown
        for rule in ["rule_a", "rule_b", "rule_c"]:
            n = self.targets[rule].sum()
            logger.info(f"  {rule}: {n} ({n/n_total*100:.1f}%)")

        return self.targets

    def build_features(self) -> pd.DataFrame:
        """Build pre-game features for all target rows."""
        logger.info("Engineering pre-game features...")
        fe = FeatureEngineer(self.gps, self.pse, self.wellness, self.sessions)
        self.features = fe.build_features(self.targets)
        logger.info(f"Features built: {self.features.shape[1] - 3} features for {len(self.features)} samples")
        return self.features

    def train_model(self, train_game_ids=None, test_game_ids=None) -> Dict:
        """Train the XGBoost model with temporal validation."""
        logger.info("Training XGBoost model...")

        # If no explicit split, use temporal ordering
        if train_game_ids is None or test_game_ids is None:
            game_sessions = self.sessions[self.sessions["is_game"]].sort_values("data")
            game_ids = game_sessions["id"].tolist()
            n_games = len(game_ids)

            if n_games < 3:
                logger.warning(f"Only {n_games} games — using all for training (no test set)")
                train_game_ids = game_ids
                test_game_ids = game_ids  # same set for now
            else:
                # Train on first ~70%, test on rest
                split = max(2, int(n_games * 0.7))
                train_game_ids = game_ids[:split]
                test_game_ids = game_ids[split:]

            logger.info(f"Temporal split: train games {train_game_ids}, test games {test_game_ids}")

        report = self.predictor.train(
            self.features, self.targets,
            train_game_ids=train_game_ids,
            test_game_ids=test_game_ids,
        )

        return report

    def predict_next_game(self, game_date=None) -> List[Dict]:
        """
        Generate pre-game predictions for all active athletes.

        Parameters
        ----------
        game_date : date of the upcoming game (default: today)

        Returns
        -------
        list of prediction dicts per athlete
        """
        if game_date is None:
            game_date = pd.Timestamp.now()
        else:
            game_date = pd.Timestamp(game_date)

        # Build features for all active athletes as if game is on game_date
        active = self.athletes[self.athletes["ativo"] == True]
        fe = FeatureEngineer(self.gps, self.pse, self.wellness, self.sessions)

        # Create dummy target rows for feature building
        dummy_targets = pd.DataFrame({
            "atleta_id": active["id"].values,
            "sessao_id": [0] * len(active),
            "data": [game_date] * len(active),
        })

        features = fe.build_features(dummy_targets)
        predictions = self.predictor.predict(features)

        # Enrich with athlete info
        results = []
        for _, pred in predictions.iterrows():
            athlete = active[active["id"] == pred["atleta_id"]]
            if athlete.empty:
                continue
            a = athlete.iloc[0]
            results.append({
                "atleta_id": int(pred["atleta_id"]),
                "nome": a["nome_completo"],
                "posicao": a["posicao"],
                "numero": a.get("numero_camisola"),
                "probability": round(float(pred["probability"]), 4),
                "severity": pred["severity"],
                "shap_factors": pred["shap_factors"],
            })

        # Sort by probability descending
        results.sort(key=lambda x: x["probability"], reverse=True)
        return results

    def run_full_pipeline(self) -> Dict:
        """Run the complete pipeline: load → target → features → train → report."""
        self.load_data()
        self.build_target()

        if self.targets.empty:
            return {
                "status": "no_data",
                "message": "No game sessions found in database. Upload game data first.",
            }

        self.build_features()
        report = self.train_model()

        return {
            "status": "success",
            "training_report": report,
            "target_summary": {
                "total_samples": len(self.targets),
                "positive_rate": round(float(self.targets["target"].mean()), 4),
                "games_analyzed": int(self.targets["sessao_id"].nunique()),
                "athletes_analyzed": int(self.targets["atleta_id"].nunique()),
                "rule_a_count": int(self.targets["rule_a"].sum()),
                "rule_b_count": int(self.targets["rule_b"].sum()),
                "rule_c_count": int(self.targets["rule_c"].sum()),
            },
        }


# ===================================================================
# Singleton for API usage
# ===================================================================
_pipeline_instance: Optional[PreGamePipeline] = None


def get_pipeline(db) -> PreGamePipeline:
    """Get or create the pipeline singleton."""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = PreGamePipeline(db)
    else:
        _pipeline_instance.db = db
        _pipeline_instance.loader = DataLoader(db)
    return _pipeline_instance
