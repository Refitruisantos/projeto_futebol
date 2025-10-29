import pandas as pd
import numpy as np

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

    dados = _engenharia_de_variaveis(dados)
    _validar_ranges(dados)
    return dados


def _engenharia_de_variaveis(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Distância em alta intensidade (>25.2 km/h) se existir coluna correspondente
    # Tenta mapear nomes comuns
    possiveis_hsr = [
        'dist_alta_intensidade',
        'dist_high_speed',
        'high_speed_distance',
        'zona_alta_vel',  # pode representar metros acima de limiar
    ]
    df['dist_alta_intensidade'] = _primeira_col_valida(df, possiveis_hsr)

    # Sprints: se existir contagem direta, usa; caso contrário, tenta proxy
    possiveis_sprints = ['sprints', 'num_sprints', 'sprints_contagem']
    df['sprints'] = _primeira_col_valida(df, possiveis_sprints)

    # FC média e máxima
    df['fc_media'] = _primeira_col_valida(df, ['fc_media', 'hr_media', 'fc_avg'])
    df['fc_max'] = _primeira_col_valida(df, ['fc_max', 'hr_max'])
    if 'fc_max' in df and df['fc_max'].isna().all() and 'fc_media' in df:
        # proxy quando não existe máxima
        df['fc_max'] = df['fc_media'] * 1.15

    # Duração da sessão (minutos) para carga relativa
    df['duracao_min'] = _primeira_col_valida(df, ['duracao_min', 'duracao', 'minutos_sessao'])
    if 'duracao_min' in df and 'distancia_total' in df:
        with np.errstate(divide='ignore', invalid='ignore'):
            df['dist_por_min'] = np.where(df['duracao_min']>0, df['distancia_total']/df['duracao_min'], np.nan)

    # Zonas de intensidade (se existirem colunas específicas)
    # Ex.: tempo_zona1..tempo_zona5 ou perc_zona1..perc_zona5
    for base in ['tempo_zona', 'perc_zona']:
        for i in range(1, 6):
            col = f'{base}{i}'
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

    # Acelerações/decelerações (>2.5 m/s²) se presente
    for c in ['aceleracoes', 'desaceleracoes']:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')

    return df


def _primeira_col_valida(df: pd.DataFrame, nomes: list):
    for n in nomes:
        if n in df.columns:
            return pd.to_numeric(df[n], errors='coerce') if df[n].dtype != 'datetime64[ns]' else df[n]
    return np.nan


def _validar_ranges(df: pd.DataFrame):
    avisos = []
    # Velocidade máxima plausível (km/h)
    if 'velocidade_max' in df.columns:
        vmax = df['velocidade_max'].max(skipna=True)
        if pd.notna(vmax) and vmax > 45:
            avisos.append(f"velocidade_max muito alta detectada: {vmax}")
    # FC plausível
    if 'fc_max' in df.columns:
        fcm = df['fc_max'].max(skipna=True)
        if pd.notna(fcm) and fcm > 230:
            avisos.append(f"fc_max muito alta detectada: {fcm}")
    # Distância por minuto plausível
    if 'dist_por_min' in df.columns:
        dpm = df['dist_por_min'].max(skipna=True)
        if pd.notna(dpm) and dpm > 200:
            avisos.append(f"dist_por_min muito alta detectada: {dpm}")
    if avisos:
        print("Avisos de validação:")
        for a in avisos:
            print(" -", a)
