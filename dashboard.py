import streamlit as st
import plotly.graph_objects as go

def render_dashboard(resumo, horario, p):
    st.header("6. RESUMO DE FLUXOS E VIABILIDADE ECONÓMICA") [cite: 75]
    
    # Cálculos Totais Anuais
    t_prod = resumo['prod_dc'].sum()
    t_cons = resumo['cons_kwh'].sum()
    t_auto = resumo['autoconsumo_kwh'].sum()
    t_imp = resumo['importacao_kwh'].sum()
    t_exc = resumo['excedente_kwh'].sum()
    
    # Linha de KPIs (Design da Foto)
    c1, c2, c3, c4, c5 = st.columns(5)
    
    with c1: # Autossuficiência (SSR) [cite: 76, 77]
        st.markdown(f"<div style='text-align:center'>🌿<br>AUTOSSUFICIÊNCIA<br><h2 style='color:#1E3A8A'>{t_auto/t_cons*100:.2f}%</h2><p style='color:#3B82F6'>{t_auto:,.2f} kWh</p></div>", unsafe_allow_html=True)
    
    with c2: # Importação [cite: 78, 80, 82]
        st.markdown(f"<div style='text-align:center'>🔌<br>IMPORTAÇÃO REDE<br><h2 style='color:#1E3A8A'>{t_imp/t_cons*100:.1f}%</h2><p style='color:#3B82F6'>{t_imp:,.2f} kWh</p></div>", unsafe_allow_html=True)

    with c3: # Excedente [cite: 79, 81, 83]
        st.markdown(f"<div style='text-align:center'>☀️<br>EXCEDENTE REDE<br><h2 style='color:#E11D48'>{t_exc/t_prod*100:.1f}%</h2><p style='color:#3B82F6'>{t_exc:,.2f} kWh</p></div>", unsafe_allow_html=True)

    with c4: # Produção Solar [cite: 90]
        st.markdown(f"<div style='text-align:center'>⚡<br>PRODUÇÃO SOLAR<br><h2 style='color:#1E3A8A'>{t_prod:,.2f}</h2><p>kWh / Ano</p></div>", unsafe_allow_html=True)

    with c5: # Rácio Autoconsumo (SCR) [cite: 91, 92]
        st.markdown(f"<div style='text-align:center'>🎯<br>RÁCIO AUTOCONSUMO<br><h2 style='color:#1E3A8A'>{t_auto/t_prod*100:.1f}%</h2><p>Eficiência Local</p></div>", unsafe_allow_html=True)

    st.markdown("---")
    
    # Gráfico de Barras Sobreposto (Relatório Pg 2)
    st.subheader("5. BALANÇO ENERGÉTICO MENSAL SIMULADO") [cite: 48]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=resumo['mes'], y=resumo['cons_kwh'], name='Consumo', marker_color='#E5E7EB')) [cite: 48]
    fig.add_trace(go.Bar(x=resumo['mes'], y=resumo['prod_dc'], name='Produção', marker_color='#3B82F6', width=0.4)) [cite: 49]
    fig.update_layout(barmode='overlay', xaxis_title="Mês", yaxis_title="Energia (kWh)")
    st.plotly_chart(fig, use_container_width=True)

    # Visualização de Bateria (SoC)
    st.subheader("🔋 Estado de Carga da Bateria (Dia Médio)")
    dia_medio = horario.groupby('hora')['soc_kwh'].mean().reset_index()
    fig_bat = go.Figure(go.Scatter(x=dia_medio['hora'], y=dia_medio['soc_kwh'], fill='tozeroy', name='SoC (kWh)', line_color='#10B981'))
    st.plotly_chart(fig_bat, use_container_width=True)
