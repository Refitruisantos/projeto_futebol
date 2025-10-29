import plotly.express as px
import pandas as pd

def mostrar_dashboard(perfis, alertas):
    if not perfis:
        print("Não há perfis de jogadores para visualizar.")
        return

    df = pd.DataFrame.from_dict(perfis, orient='index')
    df['alerta'] = df.index.map(alertas)

    # Mapeia os valores de alerta para texto mais claro
    df['alerta'] = df['alerta'].map({1: 'Risco Alto', 0: 'Risco Baixo', -1: 'Dados Insuficientes'})

    fig = px.scatter(df, x='media_distancia', y='velocidade_max',
                     color='alerta', hover_name=df.index,
                     title='Perfil Físico dos Jogadores',
                     labels={'media_distancia': 'Distância Média (m)', 'velocidade_max': 'Velocidade Máxima (km/h)'},
                     color_discrete_map={
                         'Risco Alto': 'red',
                         'Risco Baixo': 'green',
                         'Dados Insuficientes': 'grey'
                     })
    fig.show()
