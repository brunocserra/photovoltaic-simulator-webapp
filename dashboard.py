import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def render_dashboard(resumo_mensal, df_horario):
    st.header("📊 Relatório de Performance Energética")
    
    # --- Secção 1: KPIs ---
    total_clipping = resumo_mensal['clipping_kwh'].sum()
    total_prod_ac = resumo_mensal['producao_kwh'].sum()
    total_cons = resumo_mensal['consumo_casa_kwh'].sum()
    total_auto = resumo_mensal['autoconsumo_kwh'].sum()
    poupanca_anual = resumo_mensal['valor_poupado'].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Produção AC Útil", f"{total_prod_ac:,.0f} kWh")
    col2.metric("Energia Perdida (Clipping)", f"{total_clipping:,.0f} kWh", 
                delta=f"-{total_clipping/(total_prod_ac+total_clipping)*100:.1f}% Perda", delta_color="inverse")
    col3.metric("Autossuficiência", f"{(total_auto/total_cons*100):.1f} %")
    col4.metric("Poupança Estimada", f"€ {poupanca_anual:,.2f}")

    st.markdown("---")

    # --- Secção 2: Gráficos de Barras (Mensal) ---
    st.subheader("📈 Balanço Energético Mensal (com Clipping)")
    
    fig_mensal = go.Figure()
    fig_mensal.add_trace(go.Bar(x=resumo_mensal['mes'], y=resumo_mensal['autoconsumo_kwh'], 
                                name='Autoconsumo', marker_color='#27AE60'))
    fig_mensal.add_trace(go.Bar(x=resumo_mensal['mes'], y=resumo_mensal['excedente_kwh'], 
                                name='Excedente Rede', marker_color='#F1C40F'))
    fig_mensal.add_trace(go.Bar(x=resumo_mensal['mes'], y=resumo_mensal['clipping_kwh'], 
                                name='Perda Clipping', marker_color='#E74C3C'))
    
    fig_mensal.update_layout(barmode='stack', xaxis_title="Mês", yaxis_title="Energia (kWh)",
                             legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_mensal, use_container_width=True)

    # --- Secção 3: Análise de Cruzamento Horário (Dia Típico) ---
    st.subheader("🕒 Perfil de Carga vs Geração (Dia Médio de Junho)")
    
    # Filtrar Junho para mostrar o maior impacto solar/clipping
    df_junho = df_horario[df_horario['mes'] == 6].groupby('hora').mean().reset_index()
    
    fig_hourly = go.Figure()
    # Área de Produção AC Útil
    fig_hourly.add_trace(go.Scatter(x=df_junho['hora'], y=df_junho['producao_kwh'], 
                                    name='Produção AC (Inversor)', fill='tozeroy', 
                                    line_color='#FFA500', stackgroup='one'))
    # Área de Clipping (o que ficou acima do inversor)
    fig_hourly.add_trace(go.Scatter(x=df_junho['hora'], y=df_junho['clipping_kwh'], 
                                    name='Potência Cortada (Clipping)', fill='tonexty', 
                                    line_color='#E74C3C', stackgroup='one'))
    # Linha de Consumo
    fig_hourly.add_trace(go.Scatter(x=df_junho['hora'], y=df_junho['consumo_casa_kwh'], 
                                    name='Consumo Perfil', line=dict(color='#2E86C1', width=3, dash='dash')))
    
    fig_hourly.update_layout(xaxis_title="Hora do Dia", yaxis_title="Potência Média (kW)",
                             hovermode="x unified")
    st.plotly_chart(fig_hourly, use_container_width=True)

    # --- Secção 4: Tabela de Dados Brutos ---
    with st.expander("📄 Ver Matriz de Dados Mensais"):
        st.dataframe(resumo_mensal.style.format(precision=2), use_container_width=True)
