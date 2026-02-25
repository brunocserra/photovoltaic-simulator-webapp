import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def render_dashboard(resumo_mensal, df_horario):
    # --- KPIs Superiores ---
    st.subheader("📌 Indicadores Chave de Performance (KPIs)")
    c1, c2, c3, c4 = st.columns(4)
    
    prod_anual = resumo_mensal['producao_kwh'].sum()
    cons_anual = resumo_mensal['consumo_casa_kwh'].sum()
    autoconsumo = resumo_mensal['autoconsumo_kwh'].sum()
    poupanca = resumo_mensal['valor_poupado'].sum()
    
    c1.metric("Produção Anual", f"{prod_anual:,.0f} kWh", help="Energia total gerada")
    c2.metric("Independência Energética", f"{(autoconsumo/cons_anual*100):.1f} %", help="Percentagem do consumo suprido pelo solar")
    c3.metric("Poupança Estimada", f"€ {poupanca:,.2f}", help="Redução na fatura + venda de excedente")
    c4.metric("Taxa de Utilização", f"{(autoconsumo/prod_anual*100):.1f} %", help="Quanto da produção foi consumida localmente")

    st.markdown("---")

    # --- Gráfico de Cruzamento Mensal ---
    st.subheader("📈 Cruzamento Mensal: Produção vs Consumo")
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=resumo_mensal['mes'], y=resumo_mensal['producao_kwh'],
        name='Produção Solar', marker_color='#FFA500'
    ))
    fig.add_trace(go.Bar(
        x=resumo_mensal['mes'], y=resumo_mensal['consumo_casa_kwh'],
        name='Consumo Estimado', marker_color='#2E86C1'
    ))
    
    fig.update_layout(
        barmode='group', 
        xaxis_title="Mês", 
        yaxis_title="Energia (kWh)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=0)
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Gráfico de Balanço de Fluxos ---
    st.subheader("🔄 Destino da Energia Gerada")
    
    # Exemplo de Gráfico de Áreas para ver a cobertura
    fig_area = go.Figure()
    fig_area.add_trace(go.Scatter(
        x=resumo_mensal['mes'], y=resumo_mensal['autoconsumo_kwh'],
        fill='tozeroy', name='Autoconsumo', line_color='#27AE60'
    ))
    fig_area.add_trace(go.Scatter(
        x=resumo_mensal['mes'], y=resumo_mensal['excedente_kwh'],
        fill='tonexty', name='Excedente (Venda)', line_color='#F1C40F'
    ))
    
    fig_area.update_layout(title="Composição da Produção Mensal", xaxis_title="Mês", yaxis_title="kWh")
    st.plotly_chart(fig_area, use_container_width=True)
