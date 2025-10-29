import plotly.express as px
import pandas as pd

def mostrar_dashboard(perfis, alertas):
    if not perfis:
        print("Não há perfis de jogadores para visualizar.")
        return

    df = pd.DataFrame.from_dict(perfis, orient='index')
    df['__alert_raw'] = df.index.map(alertas)
    if isinstance(next(iter(alertas.values())), dict):
        df['risco'] = df['__alert_raw'].apply(lambda x: x.get('risco') if isinstance(x, dict) else -1)
        df['prob'] = df['__alert_raw'].apply(lambda x: x.get('prob') if isinstance(x, dict) else None)
    else:
        df['risco'] = df['__alert_raw']
        df['prob'] = None
    df.drop(columns=['__alert_raw'], inplace=True)

    df['alerta'] = df['risco'].map({1: 'Risco Alto', 0: 'Risco Baixo', -1: 'Dados Insuficientes'})

    fig = px.scatter(df, x='media_distancia', y='velocidade_max',
                     color='alerta', hover_name=df.index,
                     title='Perfil Físico dos Jogadores',
                     labels={'media_distancia': 'Distância Média (m)', 'velocidade_max': 'Velocidade Máxima (km/h)'},
                     hover_data={'prob': True},
                     color_discrete_map={
                         'Risco Alto': 'red',
                         'Risco Baixo': 'green',
                         'Dados Insuficientes': 'grey'
                     })
    fig.show()
