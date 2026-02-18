import os
import pandas as pd
import streamlit as st
import numpy as np
from dados import carregar_dados
from perfil_jogador import gerar_perfis, calcular_baseline, calcular_delta_ri
from modelo import treinar_modelo, prever_quebras, explicar_shap
from visualizacao import mostrar_dashboard
from datetime import datetime
from utils import segmentar_fases_jogo, agregar_janelas_5min

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
    st.markdown("---")
    st.subheader("Intra-jogo (5 min)")
    drop_pct = st.slider("Queda percentual para alerta", min_value=0, max_value=50, value=20, step=5, help="Ex.: 20% abaixo da média do jogo")
    cons_win = st.number_input("Janelas consecutivas (min)", min_value=1, max_value=5, value=2, step=1)

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
    fig_scatter = px.scatter(perfis_df, x='media_distancia', y='velocidade_max', color=perfis_df['risco'].map({1:'Risco Alto',0:'Risco Baixo',-1:'Dados Insuficientes'}), hover_name=perfis_df.index, hover_data=['prob'])
    st.plotly_chart(fig_scatter, use_container_width=True)
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
    metricas = st.multiselect("Métricas", options=["pse", "distancia_total", "sprints"], default=["pse"]) 
    roll_opt = st.selectbox("Rolling Média", options=["Sem rolling", "7 dias", "14 dias"], index=0)

    ts = df[df['jogador_id'] == sel_jog][['data'] + metricas].sort_values('data').copy()
    for m in metricas:
        ts[m] = pd.to_numeric(ts[m], errors='coerce')
    ts = ts.dropna(subset=metricas, how='all')
    if roll_opt == "7 dias":
        for m in metricas:
            ts[m + "_roll"] = ts[m].rolling(window=7, min_periods=1).mean()
    elif roll_opt == "14 dias":
        for m in metricas:
            ts[m + "_roll"] = ts[m].rolling(window=14, min_periods=1).mean()

    import plotly.express as px
    y_cols = []
    for m in metricas:
        y_cols.append(m)
        if (m + "_roll") in ts.columns:
            y_cols.append(m + "_roll")
    fig_ts = px.line(ts, x='data', y=y_cols, labels={"value":"valor","data":"data","variable":"série"})
    st.plotly_chart(fig_ts, use_container_width=True)

# Tendências agregadas por grupo com bandas p10–p90
st.subheader("Tendências por Grupo (Equipa/Posição)")
import plotly.graph_objects as go
group_field = None
if 'equipa' in df.columns or 'posicao' in df.columns:
    group_field = st.selectbox("Agrupar por", options=[opt for opt in ["equipa" if 'equipa' in df.columns else None, "posicao" if 'posicao' in df.columns else None] if opt])
    metrica_g = st.selectbox("Métrica (grupo)", options=["pse", "distancia_total", "sprints"], index=0)
    if group_field:
        gdf = df[['data', group_field, metrica_g]].copy()
        gdf[metrica_g] = pd.to_numeric(gdf[metrica_g], errors='coerce')
        gdaily = gdf.groupby(['data', group_field], as_index=False)[metrica_g].agg(['mean','quantile']).reset_index()
        # Calcular p10 e p90 manualmente por grupo/data
        stats = gdf.groupby(['data', group_field])[metrica_g].agg(mean='mean', p10=lambda x: x.quantile(0.1), p90=lambda x: x.quantile(0.9)).reset_index()
        fig_group = go.Figure()
        for grp in stats[group_field].unique():
            s = stats[stats[group_field]==grp].sort_values('data')
            fig_group.add_trace(go.Scatter(x=s['data'], y=s['p90'], mode='lines', line=dict(width=0), name=f"{grp} p90", showlegend=False))
            fig_group.add_trace(go.Scatter(x=s['data'], y=s['p10'], mode='lines', fill='tonexty', fillcolor='rgba(0, 123, 255, 0.1)', line=dict(width=0), name=f"{grp} p10-p90", showlegend=False))
            fig_group.add_trace(go.Scatter(x=s['data'], y=s['mean'], mode='lines', name=f"{grp} média"))
        fig_group.update_layout(yaxis_title=metrica_g, xaxis_title='data')
        st.plotly_chart(fig_group, use_container_width=True)
else:
    st.info("Sem colunas de equipa/posição para tendências por grupo.")

# Intra-jogo: janelas de 5 minutos e fases do jogo
st.subheader("Análise Intra-Jogo (5 min) e Fases")
required_cols = {"jogador_id", "jogo_id"}
has_time_col = ("minuto" in df.columns) or ("tempo_seg" in df.columns)
if required_cols.issubset(set(df.columns)) and has_time_col:
    df_fases = segmentar_fases_jogo(df)
    # Mostrar distribuição por fase (se disponível)
    if 'fase_jogo' in df_fases.columns:
        fase_counts = df_fases.groupby(['fase_jogo']).size().reset_index(name='registos')
        st.write("Distribuição de registos por fase:" )
        st.dataframe(fase_counts)

    met_opts = [m for m in ["dist_por_min", "sprints", "fc_media"] if m in df.columns]
    if not met_opts:
        st.info("Sem métricas intra-jogo disponíveis (procura por 'dist_por_min', 'sprints', 'fc_media').")
    else:
        met_sel = st.selectbox("Métrica intra-jogo", options=met_opts)
        win_df = agregar_janelas_5min(df, metrics=[met_sel], window_min=5, step_min=5)
        if win_df.empty:
            st.info("Sem janelas agregadas (verifica 'jogador_id', 'jogo_id' e 'minuto'/'tempo_seg').")
        else:
            # baseline do jogo por jogador: média da métrica em todas as janelas
            b = win_df.groupby(['jogador_id','jogo_id'])[met_sel].mean().rename('baseline').reset_index()
            w = win_df.merge(b, on=['jogador_id','jogo_id'], how='left')
            w['threshold'] = w['baseline'] * (1 - drop_pct/100.0)
            w['queda'] = w[met_sel] < w['threshold']
            # marcar consecutivas por jogador/jogo
            def flag_consecutive(x):
                x = x.sort_values('janela_inicio_min')
                seq = (x['queda'] & x['queda'].shift(1).fillna(False)).astype(int)
                # contar run-length; abordagem simples
                run = []
                count = 0
                prev = False
                for q in x['queda']:
                    if q:
                        count = count + 1 if prev else 1
                    else:
                        count = 0
                    run.append(count)
                    prev = q
                x['queda_seq'] = run
                return x
            w = w.groupby(['jogador_id','jogo_id'], group_keys=False).apply(flag_consecutive)
            alerts_w = w[(w['queda']) & (w['queda_seq'] >= cons_win)][['jogador_id','jogo_id','janela_inicio_min','janela_fim_min',met_sel,'baseline','threshold','queda_seq']]
            st.write("Janelas com queda detetada (regras: ", drop_pct, "%, ", cons_win, " janelas seguidas):")
            st.dataframe(alerts_w)

            # Exportações intra-jogo
            c1, c2 = st.columns(2)
            with c1:
                st.download_button(
                    label="Exportar Janelas (CSV)",
                    data=w.to_csv(index=False).encode('utf-8'),
                    file_name="intra_jogo_janelas.csv",
                    mime="text/csv"
                )
            with c2:
                st.download_button(
                    label="Exportar Quedas (CSV)",
                    data=alerts_w.to_csv(index=False).encode('utf-8'),
                    file_name="intra_jogo_quedas.csv",
                    mime="text/csv"
                )

            # Plot por jogador/jogo
            jog_plot_opts = sorted(w[['jogador_id','jogo_id']].drop_duplicates().itertuples(index=False, name=None))
            if jog_plot_opts:
                sel_pair = st.selectbox("Série intra-jogo para visualizar", options=jog_plot_opts, format_func=lambda t: f"Jogador {t[0]} - Jogo {t[1]}")
                subw = w[(w['jogador_id']==sel_pair[0]) & (w['jogo_id']==sel_pair[1])].sort_values('janela_inicio_min')
                import plotly.graph_objects as go
                figw = go.Figure()
                figw.add_trace(go.Scatter(x=subw['janela_inicio_min'], y=subw[met_sel], mode='lines+markers', name=met_sel))
                figw.add_trace(go.Scatter(x=subw['janela_inicio_min'], y=subw['threshold'], mode='lines', name='threshold', line=dict(dash='dash')))
                figw.update_layout(xaxis_title='minuto início janela', yaxis_title=met_sel)
                st.plotly_chart(figw, use_container_width=True)
else:
    st.info("Para análise intra-jogo, adiciona colunas: 'jogador_id', 'jogo_id' e 'minuto' (ou 'tempo_seg') no gps.csv.")

# Relatório HTML on-demand
st.subheader("Relatório")
def gerar_relatorio_html():
    parts = []
    parts.append("<h1>Relatório de Rendimento</h1>")
    parts.append(f"<p>Gerado em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
    try:
        parts.append("<h2>Alertas</h2>")
        parts.append(alertas_df.to_html())
    except Exception:
        pass
    try:
        if 'fig_scatter' in globals():
            parts.append("<h2>Perfil Físico (Scatter)</h2>")
            parts.append(fig_scatter.to_html(full_html=False, include_plotlyjs='cdn'))
    except Exception:
        pass
    try:
        if 'fig_ts' in locals():
            parts.append("<h2>Evolução Temporal</h2>")
            parts.append(fig_ts.to_html(full_html=False, include_plotlyjs='cdn'))
    except Exception:
        pass
    try:
        if 'fig_group' in locals():
            parts.append("<h2>Tendências por Grupo</h2>")
            parts.append(fig_group.to_html(full_html=False, include_plotlyjs='cdn'))
    except Exception:
        pass
    return "\n".join(parts).encode('utf-8')

report_bytes = gerar_relatorio_html()
st.download_button(label="Gerar Relatório (HTML)", data=report_bytes, file_name="relatorio_rendimento.html", mime="text/html")

# Risco Composto (ΔRᵢ + Intra-jogo + Probabilidade do modelo)
st.subheader("Risco Composto")
try:
    baselines_dash = calcular_baseline(df, n_datas=5)
    deltas_dash = calcular_delta_ri(df, baselines_dash, k_sessoes=3)
    # construir dataframe com probabilidade do modelo
    prob_series = alertas_df.get('prob') if 'prob' in alertas_df.columns else None
    rows = []
    for jid in df['jogador_id'].dropna().unique():
        dRi = (deltas_dash.get(jid, {}) or {}).get('delta_Ri', None)
        prob = float(prob_series.loc[jid]) if (prob_series is not None and jid in prob_series.index and pd.notna(prob_series.loc[jid])) else None
        # severidade intra-jogo: percentil de quedas por jogador (se existir)
        sev = None
        try:
            if 'w' in locals():
                subw_all = w[w['jogador_id']==jid]
                if not subw_all.empty:
                    # severidade como max((baseline - valor)/baseline)
                    sev = float(((subw_all['baseline'] - subw_all[met_sel]) / subw_all['baseline']).clip(lower=0).max())
        except Exception:
            pass
        # normalizações simples
        # |ΔRᵢ| -> [0,1] via sigmoid aproximada
        def sigmoid_scale(x):
            try:
                return float(1 / (1 + np.exp(-abs(x))))
            except Exception:
                return None
        s_dri = sigmoid_scale(dRi) if dRi is not None else None
        s_prob = prob if prob is not None else None
        s_sev = sev if sev is not None else None
        # combinar média ponderada simples (pesos iguais quando existem)
        comps = [v for v in [s_prob, s_sev, s_dri] if v is not None]
        comp_score = float(np.mean(comps)) if comps else None
        rows.append({'jogador_id': jid, 'prob': s_prob, 'intra_sev': s_sev, 'deltaRi_scaled': s_dri, 'risco_composto': comp_score})
    rc = pd.DataFrame(rows).set_index('jogador_id')
    st.dataframe(rc)
    st.download_button("Exportar Risco Composto (CSV)", data=rc.to_csv().encode('utf-8'), file_name="risco_composto.csv", mime="text/csv")
except Exception as e:
    st.warning(f"Não foi possível calcular risco composto: {e}")

# Explicabilidade (SHAP)
st.subheader("Porque este alerta? (SHAP)")
try:
    expl = explicar_shap(modelo, perfis)
    if not expl:
        st.info("SHAP não disponível para o modelo atual ou sem dados suficientes.")
    else:
        jog_opts_shap = [j for j in expl.keys()]
        sel_jog_shap = st.selectbox("Jogador para explicação", options=jog_opts_shap)
        contrib = expl[sel_jog_shap]['contribuicoes']
        top3 = expl[sel_jog_shap]['top3']
        st.write("Top 3 contribuições:", top3)
        import plotly.express as px
        dfc = pd.DataFrame({"feature": list(contrib.keys()), "valor": list(contrib.values())})
        dfc = dfc.sort_values(by='valor')
        fig_shap = px.bar(dfc, x='valor', y='feature', orientation='h', title=f"Contribuições SHAP - Jogador {sel_jog_shap}")
        st.plotly_chart(fig_shap, use_container_width=True)
except Exception as e:
    st.warning(f"Falha ao calcular/mostrar SHAP: {e}")

# KPIs e validação
st.subheader("KPIs de Validação")
st.caption("Carrega CSVs opcionais para avaliar concordância e impacto.")
colu1, colu2 = st.columns(2)
with colu1:
    up_dec = st.file_uploader("Decisões técnicas (substituições)", type=['csv'], key='decisoes')
with colu2:
    up_inj = st.file_uploader("Registos de lesões/carga", type=['csv'], key='lesoes')

try:
    if up_dec is not None:
        decis = pd.read_csv(up_dec)
        # esperado: jogador_id, jogo_id, substituted (0/1)
        cols_need = {'jogador_id','jogo_id','substituted'}
        if cols_need.issubset(set(decis.columns)) and not alertas_df.empty:
            # juntar prob/risco ao nível de jogador (se houver jogo_id, simplificação por agora)
            decis_agg = decis.groupby('jogador_id', as_index=False)['substituted'].max()
            a = alertas_df.copy()
            a['jogador_id'] = a.index
            join = decis_agg.merge(a[['jogador_id','risco']], on='jogador_id', how='left') if 'risco' in a.columns else decis_agg
            if 'risco' in join.columns:
                concord = float((join['substituted']==1).eq(join['risco']==1).mean())
                st.metric("Concordância alerta vs substituição", f"{concord*100:.1f}%")
            st.dataframe(join)
    if up_inj is not None:
        inj = pd.read_csv(up_inj)
        # exemplo esperado: jogador_id, data, tipo_lesao, dias_ausencia
        st.write("Registos de lesões/carga carregados:")
        st.dataframe(inj.head())
except Exception as e:
    st.warning(f"Não foi possível calcular KPIs: {e}")
