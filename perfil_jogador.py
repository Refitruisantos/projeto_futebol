import numpy as np
def gerar_perfis(dados):
    perfis = {}

    for jogador in dados['jogador_id'].unique():
        sub = dados[dados['jogador_id'] == jogador]
        perfil = {
            'media_distancia': sub['distancia_total'].mean(),
            'velocidade_max': sub['velocidade_max'].max(),
            'pse_medio': sub['pse'].mean(),
            'sprints_medio': sub['sprints'].mean()
        }
        if 'aceleracoes' in sub.columns:
            perfil['aceleracoes_medias'] = sub['aceleracoes'].mean()
        if 'desaceleracoes' in sub.columns:
            perfil['desaceleracoes_medias'] = sub['desaceleracoes'].mean()
        if 'zona_alta_vel' in sub.columns:
            perfil['zona_alta_vel_media'] = sub['zona_alta_vel'].mean()
        if 'fc_media' in sub.columns:
            perfil['fc_media_media'] = sub['fc_media'].mean()
        perfis[jogador] = perfil

    return perfis


# Métricas candidatas para baseline e delta (usa apenas as que existirem no dataset)
_METRICAS_BASE = [
    'distancia_total',
    'dist_por_min',
    'dist_alta_intensidade',
    'sprints',
    'aceleracoes',
    'desaceleracoes',
    'fc_media',
    'velocidade_max',
]


def calcular_baseline(dados, n_datas: int = 5):
    baselines = {}
    if dados.empty:
        return baselines
    cols = [c for c in _METRICAS_BASE if c in dados.columns]
    if not cols:
        return baselines
    for jogador, sub in dados.sort_values('data').groupby('jogador_id'):
        # primeiras n datas únicas
        datas_uniq = sub['data'].dropna().drop_duplicates().sort_values().head(n_datas)
        base = sub[sub['data'].isin(datas_uniq)]
        if base.empty:
            continue
        mean = base[cols].mean(numeric_only=True)
        std = base[cols].std(ddof=0, numeric_only=True)
        baselines[jogador] = {
            'mean': mean.to_dict(),
            'std': std.replace(0, float('nan')).to_dict(),
            'n_datas': int(len(datas_uniq))
        }
    return baselines


def calcular_delta_ri(dados, baselines: dict, k_sessoes: int = 3):
    deltas = {}
    if dados.empty or not baselines:
        return deltas
    cols = [c for c in _METRICAS_BASE if c in dados.columns]
    for jogador, sub in dados.sort_values('data').groupby('jogador_id'):
        if jogador not in baselines:
            continue
        recent_datas = sub['data'].dropna().drop_duplicates().sort_values().tail(k_sessoes)
        recente = sub[sub['data'].isin(recent_datas)]
        if recente.empty:
            continue
        rec_mean = recente[cols].mean(numeric_only=True)
        base = baselines[jogador]
        total = 0.0
        usadas = 0
        componentes = {}
        for m in cols:
            m_atual = rec_mean.get(m)
            m_base = base['mean'].get(m)
            m_std = base['std'].get(m)
            if m_atual is None or m_base is None or m_std is None or not isinstance(m_std, (int, float)):
                continue
            if np.isnan([m_atual, m_base, m_std]).any():
                continue
            if m_std == 0:
                continue
            z = (m_atual - m_base) / m_std
            componentes[m] = z
            total += z
            usadas += 1
        deltas[jogador] = {
            'delta_Ri': total,
            'componentes': componentes,
            'metricas_usadas': usadas,
        }
    return deltas
