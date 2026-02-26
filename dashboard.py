import streamlit as st
import plotly.graph_objects as go

def render_dashboard(resumo, horario, p):
    st.header("6. RESUMO DE FLUXOS E VIABILIDADE ECONÓMICA")
    
    t_prod = resumo['prod_ac_kwh'].sum()
    t_cons = resumo['cons_kwh'].sum()
    t_auto = resumo['autoconsumo_kwh'].sum()
    t_imp = resumo['importacao_kwh'].sum()
    t_exc = resumo['excedente_kwh'].sum()
    
    # KPIs Estilo SOLENERGE
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"<div style='text-align:center'>🌿<br>AUTOSSUFICIÊNCIA (SSR)<br><h2 style='color:#1E3A8A'>{t_auto/t_cons*100:.2f}%</h2><p style='color:#3B82F6'>{t_auto:,.0f} kWh</p></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div style='text-align:center'>🔌<br>IMPORTAÇÃO REDE<br><h2 style='color:#1E3A8A'>{t_imp/t_cons*100:.1f}%</h2><p style='color:#3B82F6'>{t_imp:,.0f} kWh</p></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div style='text-align:center'>☀️<br>EXCEDENTE REDE<br><h2 style='color:#E11D48'>{t_exc/t_prod*100:.1f}%</h2><p style='color:#3B82F6'>{t_exc:,.0f} kWh</p></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div style='text-align:center'>⚡<br>PRODUÇÃO SOLAR<br><h2 style='color:#1E3A8A'>{t_prod:,.0f}</h2><p>kWh / Ano</p></div>", unsafe_allow_html=True)
    with c5:
        st.markdown(f"<div style='text-align:center'>🎯<br>RÁCIO AUTOCONSUMO (SCR)<br><h2 style='color:#1E3A8A'>{t_auto/t_prod*100:.1f}%</h2><p>Eficiência Local</p></div>", unsafe_allow_html=True)

    st.markdown("---")
    
    # Gráfico Mensal Sobreposto
    st.subheader("5. BALANÇO ENERGÉTICO MENSAL SIMULADO")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=resumo['mes'], y=resumo['cons_kwh'], name='Consumo (EDA)', marker_color='#E5E7EB'))
    fig.add_trace(go.Bar(x=resumo['mes'], y=resumo['prod_ac_kwh'], name='Produção (Inversor)', marker_color='#3B82F6', width=0.4))
    fig.update_layout(barmode='overlay', xaxis_title="Mês", yaxis_title="Energia (kWh)", legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig, use_container_width=True)

    # Gráficos Sazonais Sobrepostos
    st.subheader("🕒 Perfis de Carga e Produção (Dia Médio)")
    cv, ci = st.columns(2)

    def plot_seasonal(df_filtered, title):
        df_h = df_filtered.groupby('hora').mean().reset_index()
        f = go.Figure()
        f.add_trace(go.Scatter(x=df_h['hora'], y=df_h['prod_ac_kwh'], fill='tozeroy', name='Produção AC', line_color='#FBBF24'))
        f.add_trace(go.Scatter(x=df_h['hora'], y=df_h['cons_kwh'], name='Carga', line=dict(color='#1E3A8A', width=3, dash='dash')))
        f.add_trace(go.Scatter(x=df_h['hora'], y=df_h['soc_kwh'], name='Bateria (SoC)', line_color='#10B981', yaxis="y2"))
        f.update_layout(title=title, xaxis_title="Hora", yaxis_title="kW", 
                        yaxis2=dict(title="SoC (kWh)", overlaying="y", side="right"),
                        legend=dict(orientation="h", y=-0.2), height=450)
        return f

    with cv:
        st.plotly_chart(plot_seasonal(horario[horario['mes'] == 6], "Junho (Verão)"), use_container_width=True)
    with ci:
        st.plotly_chart(plot_seasonal(horario[horario['mes'] == 12], "Dezembro (Inverno)"), use_container_width=True)
