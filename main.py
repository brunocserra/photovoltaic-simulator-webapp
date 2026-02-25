import streamlit as st
import pandas as pd
import requests
import io
from sidebar import render_sidebar
from dashboard import render_dashboard

def executar_simulacao(p):
    # Dicionário de URLs do Azure Blob Storage
    urls = {
        "A": "https://extincorpdfsstore.blob.core.windows.net/solenerge/perfil_consumo_A.csv",
        "B": "https://extincorpdfsstore.blob.core.windows.net/solenerge/perfil_consumo_B.csv",
        "C": "https://extincorpdfsstore.blob.core.windows.net/solenerge/perfil_consumo_C.csv"
    }
    
    # 1. Carregar Perfil de Consumo
    try:
        response = requests.get(urls[p['perfil']])
        response.raise_for_status()
        df_cons = pd.read_csv(io.StringIO(response.text))
    except Exception as e:
        st.error(f"Erro ao carregar perfil de consumo: {e}")
        return None, None

    # 2. Consultar API PVGIS
    # Conversão de Azimute (PVGIS usa Sul=0)
    pvgis_azim = p['azimuth'] - 180
    pvgis_url = (f"https://re.jrc.ec.europa.eu/api/v5_2/seriescalc?"
                 f"lat={p['lat']}&lon={p['lon']}&raddatabase=PVGIS-SARAH2&peakpower={p['kwp']}"
                 f"&loss=14&mountingplace=free&angle={p['inclination']}&aspect={pvgis_azim}"
                 f"&pvcalculation=1&outputformat=json")
    
    try:
        pvgis_req = requests.get(pvgis_url)
        pvgis_req.raise_for_status()
        data = pvgis_req.json()
        df_pv = pd.DataFrame(data['outputs']['hourly'])
    except Exception as e:
        st.error(f"Erro na API PVGIS: {e}")
        return None, None
    
    # 3. Tratamento de Dados e Cálculo de Clipping
    df_pv['mes'] = df_pv['time'].str[4:6].astype(int)
    df_pv['dia'] = df_pv['time'].str[6:8].astype(int)
    df_pv['hora'] = df_pv['time'].str[9:11].astype(int)
    
    # Produção bruta vinda dos painéis (DC)
    df_pv['producao_bruta_kwh'] = df_pv['P'] / 1000
    
    # Lógica de Clipping: Limitado pela potência AC do inversor
    df_pv['producao_kwh'] = df_pv['producao_bruta_kwh'].clip(upper=p['p_ac'])
    df_pv['clipping_kwh'] = (df_pv['producao_bruta_kwh'] - p['p_ac']).clip(lower=0)
    
    # Remover bissextos e calcular média horária para sincronismo com perfil ERSE
    df_pv = df_pv[~((df_pv['mes'] == 2) & (df_pv['dia'] == 29))]
    df_pv_avg = df_pv.groupby(['mes', 'dia', 'hora'])[['producao_kwh', 'clipping_kwh', 'producao_bruta_kwh']].mean().reset_index()

    # 4. Cruzamento de Simultaneidade (Produção AC vs Consumo)
    df_merged = pd.merge(df_cons, df_pv_avg, on=['mes', 'dia', 'hora'])
    df_merged['consumo_casa_kwh'] = df_merged['Peso_Horario_Mil'] * p['consumo_anual']
    
    # Autoconsumo, Importação e Excedente
    df_merged['autoconsumo_kwh'] = df_merged[['producao_kwh', 'consumo_casa_kwh']].min(axis=1)
    df_merged['importacao_kwh'] = (df_merged['consumo_casa_kwh'] - df_merged['autoconsumo_kwh']).clip(lower=0)
    df_merged['excedente_kwh'] = (df_merged['producao_kwh'] - df_merged['autoconsumo_kwh']).clip(lower=0)

    # 5. Agregação Mensal para o Dashboard
    resumo = df_merged.groupby('mes').agg({
        'producao_kwh': 'sum',
        'clipping_kwh': 'sum',
        'producao_bruta_kwh': 'sum',
        'consumo_casa_kwh': 'sum',
        'autoconsumo_kwh': 'sum',
        'importacao_kwh': 'sum',
        'excedente_kwh': 'sum'
    }).reset_index()

    # Valorização Económica
    resumo['valor_pago_rede'] = resumo['importacao_kwh'] * p['preco_compra']
    resumo['valor_poupado'] = (resumo['autoconsumo_kwh'] * p['preco_compra']) + (resumo['excedente_kwh'] * p['preco_venda'])
    
    return resumo, df_merged

# --- Inicialização da App ---
st.set_page_config(page_title="PV Sim Azores Pro", layout="wide", page_icon="☀️")

run_sim, params = render_sidebar()

if run_sim:
    with st.spinner("A processar matrizes energéticas e limites de inversão..."):
        resumo_mensal, df_horario = executar_simulacao(params)
        
        if resumo_mensal is not None:
            render_dashboard(resumo_mensal, df_horario)
else:
    st.info("Configure o sistema fotovoltaico na barra lateral para iniciar a análise.")
