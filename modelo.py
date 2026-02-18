import numpy as np
from sklearn.ensemble import RandomForestClassifier
import os
from sklearn.linear_model import LogisticRegression
import shap

def treinar_modelo(perfis, model_type: str = 'rf'):
    X = []
    y = []

    if not perfis:
        return RandomForestClassifier()

    feature_names = [
        'media_distancia',
        'velocidade_max',
        'pse_medio',
        'sprints_medio',
        'aceleracoes_medias',
        'desaceleracoes_medias',
        'zona_alta_vel_media',
        'fc_media_media',
    ]

    thr = float(os.environ.get('RISCO_PSE_THRESHOLD', '7'))

    for _, perfil in perfis.items():
        row = [perfil.get(k, np.nan) for k in feature_names]
        X.append(row)
        pse_med = perfil.get('pse_medio', np.nan)
        y.append(1 if (not np.isnan(pse_med) and pse_med > thr) else 0)

    X = np.array(X, dtype=float)
    col_means = np.nanmean(X, axis=0)
    inds = np.where(np.isnan(X))
    X[inds] = np.take(col_means, inds[1])

    if X.size == 0:
        return RandomForestClassifier()

    if (model_type or '').lower() in ['logreg', 'logistic', 'lr']:
        modelo = LogisticRegression(max_iter=1000, solver='lbfgs', class_weight='balanced', random_state=42)
        modelo.fit(X, y)
    else:
        modelo = RandomForestClassifier(random_state=42)
        modelo.fit(X, y)
    modelo.feature_names_ = feature_names
    modelo.col_means_ = col_means
    return modelo

def prever_quebras(modelo, perfis):
    alertas = {}

    for jogador, perfil in perfis.items():
        if not hasattr(modelo, "classes_"):
            alertas[jogador] = -1
            continue

        fn = getattr(modelo, 'feature_names_', None)
        cm = getattr(modelo, 'col_means_', None)
        if fn is None or cm is None:
            alertas[jogador] = -1
            continue

        row = np.array([[perfil.get(k, np.nan) for k in fn]], dtype=float)
        mask = np.isnan(row)
        if mask.any():
            row[mask] = cm[np.where(mask)[1]]

        if hasattr(modelo, 'predict_proba'):
            proba = float(modelo.predict_proba(row)[0][1])
            risco = int(proba >= 0.5)
            alertas[jogador] = {"risco": risco, "prob": proba}
        else:
            risco = int(modelo.predict(row)[0])
            alertas[jogador] = {"risco": risco, "prob": None}

    return alertas

def explicar_shap(modelo, perfis):
    explicacoes = {}
    if not hasattr(modelo, "classes_"):
        return explicacoes
    fn = getattr(modelo, 'feature_names_', None)
    cm = getattr(modelo, 'col_means_', None)
    if fn is None or cm is None:
        return explicacoes
    # construir matriz X na mesma ordem das features
    jogadores = list(perfis.keys())
    X = np.array([[perfis[j].get(k, np.nan) for k in fn] for j in jogadores], dtype=float)
    mask = np.isnan(X)
    if mask.any():
        X[mask] = cm[np.where(mask)[1]]

    try:
        if isinstance(modelo, RandomForestClassifier):
            explainer = shap.TreeExplainer(modelo)
            shap_values = explainer.shap_values(X)
            # classe 1 (risco): índice 1
            sv = shap_values[1] if isinstance(shap_values, list) else shap_values
        elif isinstance(modelo, LogisticRegression):
            explainer = shap.LinearExplainer(modelo, X, feature_perturbation="interventional")
            sv = explainer.shap_values(X)
        else:
            return explicacoes
        # mapear por jogador
        for i, jid in enumerate(jogadores):
            contrib = {fn[k]: float(sv[i, k]) for k in range(len(fn))}
            # ordenar por importância absoluta
            top = sorted(contrib.items(), key=lambda x: abs(x[1]), reverse=True)
            explicacoes[jid] = {
                'contribuicoes': contrib,
                'top3': top[:3]
            }
    except Exception:
        # sem SHAP disponível para este modelo/ambiente
        pass
    return explicacoes
