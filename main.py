import streamlit as st
from sidebar import render_sidebar
from dashboard import render_dashboard
# Importe aqui a sua função de cálculo/simulador que trata o PVGIS

st.set_page_config(page_title="PV Sim Azores", layout="wide")

run_sim, params = render_sidebar()

if run_sim:
    # 1. Chamar a lógica de cálculo (aquela que estava no Flask)
    # resumo, df_horario = executar_calculos_pvgis(params)
    
    # 2. Renderizar o Dashboard no lado direito
    # render_dashboard(resumo, df_horario)
    st.success("Simulação concluída com sucesso!")
else:
    st.info("Configure os parâmetros à esquerda e clique em 'Executar Simulação'.")
