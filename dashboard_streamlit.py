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

col1, col2, col3 = st.columns(3)
with col1:
    st.download_button(
        label="Exportar Perfis (CSV)",
        data=pd.DataFrame.from_dict(perfis, orient='index').to_csv(index=True).encode('utf-8'),
        file_name="perfis.csv",
        mime="text/csv"
    )
with col2:
    st.download_button(
        label="Exportar Alertas (CSV)",
        data=alertas_df.to_csv(index=True).encode('utf-8'),
        file_name="alertas.csv",
        mime="text/csv"
    )
with col3:
    st.download_button(
        label="Exportar Dados Filtrados (CSV)",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name="dados_filtrados.csv",
        mime="text/csv"
    )

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

st.subheader("Evolução Temporal por Jogador")
if df.empty:
    st.info("Sem dados para séries temporais com os filtros atuais.")
else:
    jog_opts = sorted(df['jogador_id'].unique())
    sel_jog = st.selectbox("Jogador", options=jog_opts)
    metrica = st.selectbox("Métrica", options=["pse", "distancia_total", "sprints"], index=0)
    roll_opt = st.selectbox("Rolling Média", options=["Sem rolling", "7 dias", "14 dias"], index=0)

    ts = df[df['jogador_id'] == sel_jog][['data', metrica]].sort_values('data').copy()
    ts = ts.dropna(subset=[metrica])
    if roll_opt == "7 dias":
        ts[metrica + "_roll"] = ts[metrica].rolling(window=7, min_periods=1).mean()
    elif roll_opt == "14 dias":
        ts[metrica + "_roll"] = ts[metrica].rolling(window=14, min_periods=1).mean()

    import plotly.express as px
    if (metrica + "_roll") in ts.columns:
        fig_ts = px.line(ts, x='data', y=[metrica, metrica+"_roll"], labels={"value":"valor","data":"data","variable":"série"})
    else:
        fig_ts = px.line(ts, x='data', y=metrica)
    st.plotly_chart(fig_ts, use_container_width=True)
