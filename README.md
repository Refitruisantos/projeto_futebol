# Projeto: Monitorização de Rendimento Físico e Tático (Futebol)

Sistema modular para monitorizar jogadores com dados GPS + PSE, perfis agregados, modelo preditivo (RandomForest) e dashboard Plotly.

## Estrutura
```
projeto_futebol/
├── dados/                 # Coloca aqui gps.csv e pse.csv
├── main.py                # Script principal
├── dados.py               # Carregamento e merge GPS + PSE
├── perfil_jogador.py      # Perfis por jogador
├── modelo.py              # Treino e previsão de risco
├── visualizacao.py        # Dashboard Plotly
├── utils.py               # Funções auxiliares
└── requirements.txt       # Dependências
```

## Dados esperados
- `dados/gps.csv`: colunas `jogador_id,data,distancia_total,velocidade_max,sprints,...`
- `dados/pse.csv`: colunas `jogador_id,data,pse`
- Os `.csv` em `dados/` estão ignorados no git por omissão.

## Como executar
1. Instalar dependências (Windows):
```
python -m pip install -r requirements.txt
```
2. Executar o projeto:
```
python main.py
```

## Notas
- O modelo marca risco alto se `pse_medio > 7` (ajustável em `modelo.py`).
- O dashboard abre com um scatter de distancia vs velocidade_max, colorido por risco.
