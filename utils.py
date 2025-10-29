import pandas as pd
import numpy as np
# Aqui podem ficar funções auxiliares como limpeza de dados, conversões, etc.

def normalizar_valores(df, colunas):
    for col in colunas:
        df[col] = (df[col] - df[col].mean()) / df[col].std()
    return df


def segmentar_fases_jogo(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    if 'minuto' in d.columns:
        minuto = pd.to_numeric(d['minuto'], errors='coerce')
    elif 'tempo_seg' in d.columns:
        minuto = pd.to_numeric(d['tempo_seg'], errors='coerce') // 60
    else:
        return d
    d['__minuto__'] = minuto.astype('Int64')
    bins = [-1, 30, 75, 1000]
    labels = ['0-30', '30-75', '75-90+']
    d['fase_jogo'] = pd.cut(d['__minuto__'].astype(float), bins=bins, labels=labels)
    return d


def agregar_janelas_5min(df: pd.DataFrame, metrics: list, window_min: int = 5, step_min: int = 5) -> pd.DataFrame:
    required = {'jogador_id', 'jogo_id'}
    if not required.issubset(set(df.columns)):
        return pd.DataFrame()
    if 'minuto' in df.columns:
        minuto = pd.to_numeric(df['minuto'], errors='coerce')
    elif 'tempo_seg' in df.columns:
        minuto = pd.to_numeric(df['tempo_seg'], errors='coerce') // 60
    else:
        return pd.DataFrame()
    d = df.copy()
    d['__minuto__'] = minuto.astype('Int64')
    d = d.dropna(subset=['__minuto__'])
    for m in metrics:
        if m in d.columns:
            d[m] = pd.to_numeric(d[m], errors='coerce')
    results = []
    for (jid, gid), g in d.groupby(['jogador_id', 'jogo_id']):
        g = g.sort_values('__minuto__')
        min_m = int(g['__minuto__'].min())
        max_m = int(g['__minuto__'].max())
        starts = list(range(max(0, min_m), max_m + 1, step_min))
        for s in starts:
            e = s + window_min - 1
            w = g[(g['__minuto__'] >= s) and (g['__minuto__'] <= e)]
            # Use bitwise ops for pandas filtering
            w = g[(g['__minuto__'] >= s) & (g['__minuto__'] <= e)]
            if w.empty:
                continue
            row = {'jogador_id': jid, 'jogo_id': gid, 'janela_inicio_min': s, 'janela_fim_min': e}
            for m in metrics:
                if m in w.columns:
                    row[m] = w[m].mean(skipna=True)
            results.append(row)
    return pd.DataFrame(results)
