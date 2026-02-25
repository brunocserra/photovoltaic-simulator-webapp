import streamlit as st
import plotly.graph_objects as go

def render_dashboard(resumo, horario, p):
    st.header("6. RESUMO DE FLUXOS E VIABILIDADE ECONÓMICA")
    
    t_prod = resumo['prod_dc'].sum()
    t_cons = resumo['cons_kwh'].sum()
    t_auto = resumo['autoconsumo_kwh'].sum()
    t_imp = resumo['importacao_kwh'].sum()
    t_exc = resumo['excedente_kwh'].sum()
    
    # KPIs Estilo SOLENERGE
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"<div style='text-align:center'>🌿<br>AUTOSSUFICIÊNCIA<br><h2 style='color:#1E3A8A'>{t_auto/t_cons*100:.2f}%</h2><p style='color:#3B82F6'>{t_auto:,.0f} kWh</p></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div style='text-align:center'>🔌<br>IMPORTAÇÃO REDE<br><h2 style='color:#1E3A8A'>{t_imp/t_cons*100:.1f}%</h2><p style='color:#3B82F6'>{t_imp:,.0f} kWh</p></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div style='text-align:center'>☀️<br>EXCEDENTE REDE<br><h2 style='color:#E11D48'>{t_exc/t_prod*100:.1f}%</h2><p style='color:#3B82F6'>{t_exc:,.0f} kWh</p></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div style='text-align:center'>⚡<br>PRODUÇÃO SOLAR<br><h2 style='color:#1E3A8A'>{t_prod:,.0f}</h2><p>kWh / Ano</p></div>", unsafe_allow_html=True)
    with c5:
        st.markdown(f"<div style='text-align:center'>🎯<br>RÁCIO AUTOCONSUMO<br><h2 style='color:#1E3A8A'>{t_auto/t_prod*100:.1f}%</h2><p>Eficiência Local</p></div>", unsafe_allow_html=True)

    st.markdown("---")
    
    # Gráfico Mensal Sobreposto
    st.subheader("5. BALANÇO ENERGÉTICO MENSAL SIMULADO")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=resumo['mes'], y=resumo['cons_kwh'], name='Consumo EDA', marker_color='#E5E7EB'))
    fig.add_trace(go.Bar(x=resumo['mes'], y=resumo['prod_dc'], name='Produção PVGIS', marker_color='#3B82F6', width=0.4))
    fig.update_layout(barmode='overlay', xaxis_title="Mês", yaxis_title="Energia (kWh)", legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig, use_
