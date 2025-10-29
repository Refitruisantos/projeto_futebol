import os
import pandas as pd
import streamlit as st
from dados import carregar_dados
from perfil_jogador import gerar_perfis
from modelo import treinar_modelo, prever_quebras
from visualizacao import mostrar_dashboard
from datetime import datetime

st.set_page_config(page_title="Dashboard Rendimento - Futebol", layout="wide")

st.title("Monitorização de Rendimento Físico e Tático")

with st.sidebar:
    st.header("Filtros e Opções")
    thr = st.number_input("Threshold PSE (RISCO)", value=float(os.environ.get("RISCO_PSE_THRESHOLD", 7)), step=0.1)
    os.environ["RISCO_PSE_THRESHOLD"] = str(thr)

    model_type = st.selectbox("Modelo", options=["rf", "logreg"], index=0)

    dados = carregar_dados()
    jogadores = sorted(dados["jogador_id"].unique())
    sel_jogs = st.multiselect("Jogadores", options=jogadores, default=jogadores)

    mind = dados["data"].min()
    maxd = dados["data"].max()
    drange = st.date_input("Intervalo de Datas", value=(mind, maxd))

    extra_filters = {}
    if 'posicao' in dados.columns:
        pos_opts = sorted([p for p in dados['posicao'].dropna().unique()])
        sel_pos = st.multiselect("Posição", options=pos_opts, default=pos_opts)
        extra_filters['posicao'] = sel_pos
    if 'equipa' in dados.columns:
        team_opts = sorted([t for t in dados['equipa'].dropna().unique()])
        sel_team = st.multiselect("Equipa", options=team_opts, default=team_opts)
        extra_filters['equipa'] = sel_team

    st.caption("Dica: Exporta os dados do Catapult e coloca os ficheiros em dados/gps.csv e dados/pse.csv")

if sel_jogs:
    df = dados[dados["jogador_id"].isin(sel_jogs)].copy()
else:
    df = dados.copy()

if isinstance(drange, (list, tuple)) and len(drange) == 2:
    di, dfim = pd.to_datetime(drange[0]), pd.to_datetime(drange[1])
    df = df[(df["data"] >= di) & (df["data"] <= dfim)]

if 'posicao' in df.columns and 'posicao' in locals() and extra_filters.get('posicao') is not None:
    if extra_filters['posicao']:
        df = df[df['posicao'].isin(extra_filters['posicao'])]
if 'equipa' in df.columns and 'equipa' in locals() and extra_filters.get('equipa') is not None:
    if extra_filters['equipa']:
        df = df[df['equipa'].isin(extra_filters['equipa'])]

perfis = gerar_perfis(df)
modelo = treinar_modelo(perfis, model_type=model_type)
alertas = prever_quebras(modelo, perfis)

try:
    os.makedirs('outputs', exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    pd.DataFrame.from_dict(perfis, orient='index').to_csv(f"outputs/perfis_{ts}.csv")
    pd.DataFrame.from_dict(alertas, orient='index').to_csv(f"outputs/alertas_{ts}.csv")
except Exception as e:
    st.warning(f"Não foi possível guardar outputs: {e}")

st.subheader("Alertas por Jogador")
alertas_df = pd.DataFrame.from_dict(alertas, orient="index")
alertas_df.index.name = "jogador_id"
st.dataframe(alertas_df)

st.subheader("Perfil Físico")
try:
    from plotly.subplots import make_subplots
    import plotly.express as px
    perfis_df = pd.DataFrame.from_dict(perfis, orient='index')
    perfis_df['risco'] = perfis_df.index.map(lambda j: alertas.get(j, {}).get('risco') if isinstance(alertas.get(j), dict) else alertas.get(j))
    perfis_df['prob'] = perfis_df.index.map(lambda j: alertas.get(j, {}).get('prob') if isinstance(alertas.get(j), dict) else None)
    fig = px.scatter(perfis_df, x='media_distancia', y='velocidade_max', color=perfis_df['risco'].map({1:'Risco Alto',0:'Risco Baixo',-1:'Dados Insuficientes'}), hover_name=perfis_df.index, hover_data=['prob'])
    st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.warning(f"Não foi possível renderizar o gráfico: {e}")

with st.expander("Dados Filtrados"):
    st.dataframe(df)
