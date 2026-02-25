import streamlit as st
import pandas as pd
import requests
import io
from sidebar import render_sidebar
from dashboard import render_dashboard

st.set_page_config(page_title="PV Sim Azores", layout="wide", page_icon="☀️")

# --- Lógica de Cálculo (Originalmente do Flask) ---
def executar_simulacao(p):
    # 1. Carregar Perfil
    url_perfil = "https://raw.githubusercontent.com/brunocserra/photovoltaic-simulator/main/perfil_consumo_C.csv"
    df_cons = pd.read_csv(url_perfil)

    # 2. API PVGIS
    pvgis_azim = p['azimuth'] - 180
    pvgis_url = (f"https://re.jrc.ec.europa.eu/api/v5_2/seriescalc?"
                 f"lat={p['lat']}&lon={p['lon']}&raddatabase=PVGIS-SARAH2&peakpower={p['kwp']}"
                 f"&loss=14&mountingplace=free&angle={p['inclination']}&aspect={pvgis_azim}"
                 f"&pvcalculation=1&outputformat=json")
    
    resp = requests.get(pvgis_url).json()
    df_pv = pd.DataFrame(resp['outputs']['hourly'])
    
    # 3. Tratamento
    df_pv['mes'] = df_pv['time'].str[4:6].astype(int)
    df_pv['dia'] = df_pv['time'].str[6:8].astype(int)
    df_pv['hora'] = df_pv['time'].str[9:11].astype(int)
    df_pv['producao_kwh'] = df_pv['P'] / 1000
    df_pv = df_pv[~((df_pv['mes'] == 2) & (df_pv['dia'] == 29))]
    df_pv_avg = df_pv.groupby(['mes', 'dia', 'hora'])['producao_kwh'].mean().reset_index()

    # 4. Cruzamento
    df_merged = pd.merge(df_cons, df_pv_avg, on=['mes', 'dia', 'hora'])
    df_merged['consumo_casa_kwh'] = df_merged['Peso_Horario_Mil'] * p['consumo_anual']
    df_merged['autoconsumo_kwh'] = df_merged[['producao_kwh', 'consumo_casa_kwh']].min(axis=1)
    df_merged['importacao_kwh'] = (df_merged['consumo_casa_kwh'] - df_merged['autoconsumo_kwh']).clip(lower=0)
    df_merged['excedente_kwh'] = (df_merged['producao_kwh'] - df_merged['autoconsumo_kwh']).clip(lower=0)

    # 5. Agregação
    resumo = df_merged.groupby('mes').agg({
        'producao_kwh': 'sum',
        'consumo_casa_kwh': 'sum',
        'autoconsumo_kwh': 'sum',
        'importacao_kwh': 'sum',
        'excedente_kwh': 'sum'
    }).reset_index()

    resumo['valor_pago'] = resumo['importacao_kwh'] * p['preco_compra']
    resumo['valor_poupado'] = (resumo['autoconsumo_kwh'] * p['preco_compra']) + (resumo['excedente_kwh'] * p['preco_venda'])
    
    return resumo, df_merged

# --- Execução da App ---
run_sim, params = render_sidebar()

if run_sim:
    try:
        with st.spinner("A consultar dados PVGIS e processar matrizes..."):
            resumo_mensal, df_completo = executar_simulacao(params)
            render_dashboard(resumo_mensal, df_completo)
    except Exception as e:
        st.error(f"Erro técnico na simulação: {e}")
else:
    st.info("Altere os parâmetros técnicos no menu lateral e clique em 'Executar Simulação'.")
