import streamlit as st
import pandas as pd
import requests
import io
from sidebar import render_sidebar
from dashboard import render_dashboard

def executar_simulacao(p):
    # Dicionário com os novos links do Azure
    urls = {
        "A": "https://extincorpdfsstore.blob.core.windows.net/solenerge/perfil_consumo_A.csv",
        "B": "https://extincorpdfsstore.blob.core.windows.net/solenerge/perfil_consumo_B.csv",
        "C": "https://extincorpdfsstore.blob.core.windows.net/solenerge/perfil_consumo_C.csv"
    }
    
    # 1. Carregar Perfil do Azure
    try:
        response = requests.get(urls[p['perfil']])
        response.raise_for_status() # Lança erro se não for 200
        df_cons = pd.read_csv(io.StringIO(response.text))
    except Exception as e:
        st.error(f"Erro ao carregar perfil {p['perfil']} do Azure: {e}")
        return None, None

    # 2. API PVGIS (Lógica de Azimute Sul=0)
    pvgis_azim = p['azimuth'] - 180
    pvgis_url = (f"https://re.jrc.ec.europa.eu/api/v5_2/seriescalc?"
                 f"lat={p['lat']}&lon={p['lon']}&raddatabase=PVGIS-SARAH2&peakpower={p['kwp']}"
                 f"&loss=14&mountingplace=free&angle={p['inclination']}&aspect={pvgis_azim}"
                 f"&pvcalculation=1&outputformat=json")
    
    try:
        pvgis_req = requests.get(pvgis_url)
        pvgis_req.raise_for_status()
        df_pv = pd.DataFrame(pvgis_req.json()['outputs']['hourly'])
    except Exception as e:
        st.error(f"Erro na API PVGIS: {e}")
        return None, None
    
    # 3. Tratamento e Cruzamento (Data Science)
    df_pv['mes'] = df_pv['time'].str[4:6].astype(int)
    df_pv['dia'] = df_pv['time'].str[6:8].astype(int)
    df_pv['hora'] = df_pv['time'].str[9:11].astype(int)
    df_pv['producao_kwh'] = df_pv['P'] / 1000
    df_pv = df_pv[~((df_pv['mes'] == 2) & (df_pv['dia'] == 29))]
    df_pv_avg = df_pv.groupby(['mes', 'dia', 'hora'])['producao_kwh'].mean().reset_index()

    df_merged = pd.merge(df_cons, df_pv_avg, on=['mes', 'dia', 'hora'])
    df_merged['consumo_casa_kwh'] = df_merged['Peso_Horario_Mil'] * p['consumo_anual']
    
    # Cálculos de simultaneidade (Autoconsumo vs Excedente)
    df_merged['autoconsumo_kwh'] = df_merged[['producao_kwh', 'consumo_casa_kwh']].min(axis=1)
    df_merged['importacao_kwh'] = (df_merged['consumo_casa_kwh'] - df_merged['autoconsumo_kwh']).clip(lower=0)
    df_merged['excedente_kwh'] = (df_merged['producao_kwh'] - df_merged['autoconsumo_kwh']).clip(lower=0)

    # 4. Agregação Mensal
    resumo = df_merged.groupby('mes').agg({
        'producao_kwh': 'sum',
        'consumo_casa_kwh': 'sum',
        'autoconsumo_kwh': 'sum',
        'importacao_kwh': 'sum',
        'excedente_kwh': 'sum'
    }).reset_index()

    resumo['valor_poupado'] = (resumo['autoconsumo_kwh'] * p['preco_compra']) + (resumo['excedente_kwh'] * p['preco_venda'])
    
    return resumo, df_merged

# Execução principal
run_sim, params = render_sidebar()
if run_sim:
    resumo_mensal, df_completo = executar_simulacao(params)
    if resumo_mensal is not None:
        render_dashboard(resumo_mensal, df_completo)
