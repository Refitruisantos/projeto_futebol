import numpy as np
from sklearn.ensemble import RandomForestClassifier
import os
from sklearn.linear_model import LogisticRegression

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
