import streamlit as st
import plotly.graph_objects as go

def render_dashboard(resumo, horario, p):
    # --- SECÇÃO 6: KPIs (Estilo SOLENERGE) ---
    st.header("6. RESUMO DE FLUXOS E VIABILIDADE ECONÓMICA") # [cite: 75]
    
    t_prod = resumo['prod_dc'].sum() # [cite: 90]
    t_cons = resumo['cons_kwh'].sum() # [cite: 54]
    t_auto = resumo['autoconsumo_kwh'].sum() # [cite: 77]
    t_imp = resumo['importacao_kwh'].sum() # [cite: 82]
    t_exc = resumo['excedente_kwh'].sum() # [cite: 83]
    
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"<div style='text-align:center'>🌿<br>AUTOSSUFICIÊNCIA (SSR)<br><h2 style='color:#1E3A8A'>{t_auto/t_cons*100:.1f}%</h2><p style='color:#3B82F6'>{t_auto:,.0f} kWh</p></div>", unsafe_allow_html=True) # [cite: 76, 77]
    with c2:
        st.markdown(f"<div style='text-align:center'>🔌<br>IMPORTAÇÃO REDE<br><h2 style='color:#1E3A8A'>{t_imp/t_cons*100:.1f}%</h2><p style='color:#3B82F6'>{t_imp:,.0f} kWh</p></div>", unsafe_allow_html=True) # [cite: 78, 80, 82]
    with c3:
        st.markdown(f"<div style='text-align:center'>☀️<br>EXCEDENTE REDE<br><h2 style='color:#E11D48'>{t_exc/t_prod*100:.1f}%</h2><p style='color:#3B82F6'>{t_exc:,.0f} kWh</p></div>", unsafe_allow_html=True) # [cite: 79, 81, 83]
    with c4:
        st.markdown(f"<div style='text-align:center'>⚡<br>PRODUÇÃO SOLAR<br><h2 style='color:#1E3A8A'>{t_prod:,.0f}</h2><p>kWh / Ano</p></div>", unsafe_allow_html=True) # [cite: 90]
    with c5:
        st.markdown(f"<div style='text-align:center'>🎯<br>RÁCIO AUTOCONSUMO (SCR)<br><h2 style='color:#1E3A8A'>{t_auto/t_prod*100:.1f}%</h2><p>Eficiência Local</p></div>", unsafe_allow_html=True) # [cite: 91, 92]

    st.markdown("---")

    # --- SECÇÃO 5: BALANÇO MENSAL ---
    st.subheader("5. BALANÇO ENERGÉTICO MENSAL SIMULADO") # [cite: 48]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=resumo['mes'], y=resumo['cons_kwh'], name='Consumo EDA', marker_color='#E5E7EB')) # [cite: 48, 53]
    fig.add_trace(go.Bar(x=resumo['mes'], y=resumo['prod_dc'], name='Produção PVGIS', marker_color='#3B82F6', width=0.4)) # [cite: 49, 98]
    fig.update_layout(barmode='overlay', xaxis_title="Mês", yaxis_title="Energia (kWh)", legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig, use_container_width=True)

    # --- NOVA SECÇÃO: ANÁLISE SAZONAL HORÁRIA ---
    st.subheader("🕒 Análise Sazonal: Dia Típico (Verão vs Inverno)")
    
    col_v, col_i = st.columns(2)

    def plot_dia_tipico(df_mes, titulo):
        df_avg = df_mes.groupby('hora').mean().reset_index()
        fig_dia = go.Figure()
        # Produção AC
        fig_dia.add_trace(go.Scatter(x=df_avg['hora'], y=df_avg['prod_util_kwh'], fill='tozeroy', 
                                    name='Produção AC', line_color='#FBBF24'))
        # Carga
        fig_dia.add_trace(go.Scatter(x=df_avg['hora'], y=df_avg['cons_kwh'], 
                                    name='Carga', line=dict(color='#1E3A8A', width=3, dash='dash')))
        # SoC Bateria
        fig_dia.add_trace(go.Scatter(x=df_avg['hora'], y=df_avg['soc_kwh'], name='Bateria (SoC)', 
                                    line_color='#10B981', yaxis="y2"))
        
        fig_dia.update_layout(title=titulo, xaxis_title="Hora", yaxis_title="kW",
                             yaxis2=dict(title="SoC (kWh)", overlaying="y", side="right"),
                             legend=dict(orientation="h", y=-0.2), height=400)
        return fig_dia

    with col_v:
        # Junho (Verão)
        fig_jun = plot_dia_tipico(horario[horario['mes'] == 6], "Junho (Pico Solar)")
        st.plotly_chart(fig_jun, use_container_width=True)

    with col_i:
        # Dezembro (Inverno)
        fig_dez = plot_dia_tipico(horario[horario['mes'] == 12], "Dezembro (Baixa Irradiância)")
        st.plotly_chart(fig_dez, use_container_width=True)
