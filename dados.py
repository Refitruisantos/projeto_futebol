import pandas as pd

def carregar_dados(gps_path='dados/gps.csv', pse_path='dados/pse.csv'):
    # Carrega dados GPS e PSE reais
    gps = pd.read_csv(gps_path, parse_dates=['data'])
    pse = pd.read_csv(pse_path, parse_dates=['data'])

    # Verifica se há colunas esperadas
    colunas_esperadas = ['jogador_id', 'data', 'distancia_total', 'velocidade_max', 'sprints']
    for col in colunas_esperadas:
        if col not in gps.columns:
            raise ValueError(f"Coluna {col} não encontrada em gps.csv")

    # Junta os dados
    dados = pd.merge(gps, pse, on=['jogador_id', 'data'], how='left')

    # Preenche PSE faltante com média por jogador (caso não tenha sido preenchido no dia)
    dados['pse'] = dados.groupby('jogador_id')['pse'].transform(lambda x: x.fillna(x.mean()))
    
    # Remove linhas onde o PSE ainda é NaN (caso um jogador não tenha nenhum registo de PSE)
    dados.dropna(subset=['pse'], inplace=True)

    return dados
