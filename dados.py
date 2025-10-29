import pandas as pd

def carregar_dados(gps_path='dados/gps.csv', pse_path='dados/pse.csv'):
    gps = pd.read_csv(gps_path)
    pse = pd.read_csv(pse_path)

    if 'data' not in gps.columns:
        raise ValueError("Coluna 'data' não encontrada em gps.csv")
    if 'data' not in pse.columns:
        raise ValueError("Coluna 'data' não encontrada em pse.csv")

    gps['data'] = pd.to_datetime(gps['data'], errors='coerce')
    pse['data'] = pd.to_datetime(pse['data'], errors='coerce')
    if gps['data'].isna().any() or pse['data'].isna().any():
        raise ValueError("Datas inválidas detetadas. Use formato AAAA-MM-DD.")

    colunas_obrigatorias = ['jogador_id', 'data', 'distancia_total', 'velocidade_max', 'sprints']
    for col in colunas_obrigatorias:
        if col not in gps.columns:
            raise ValueError(f"Coluna {col} não encontrada em gps.csv")

    cols_num = [c for c in ['distancia_total','velocidade_max','sprints','aceleracoes','desaceleracoes','zona_alta_vel','fc_media'] if c in gps.columns]
    for c in cols_num:
        gps[c] = pd.to_numeric(gps[c], errors='coerce')

    pse['pse'] = pd.to_numeric(pse['pse'], errors='coerce')

    dados = pd.merge(gps, pse, on=['jogador_id', 'data'], how='left')

    dados['pse'] = dados.groupby('jogador_id')['pse'].transform(lambda x: x.fillna(x.mean()))
    dados = dados.dropna(subset=['pse'])

    dados = dados.sort_values(by=['jogador_id', 'data']).reset_index(drop=True)
    return dados
