import streamlit as st
import pandas as pd
import requests
import io
from sidebar import render_sidebar
from dashboard import render_dashboard

def executar_simulacao(p):
    urls = {"A": "https://extincorpdfsstore.blob.core.windows.net/solenerge/perfil_consumo_A.csv",
            "B": "https://extincorpdfsstore.blob.core.windows.net/solenerge/perfil_consumo_B.csv",
            "C": "https://extincorpdfsstore.blob.core.windows.net/solenerge/perfil_consumo_C.csv"}
    
    # 1. Dados e PVGIS
    res = requests.get(urls[p['perfil']])
    df_cons = pd.read_csv(io.StringIO(res.text))
    
    pvgis_url = (f"https://re.jrc.ec.europa.eu/api/v5_2/seriescalc?lat={p['lat']}&lon={p['lon']}"
                 f"&peakpower={p['kwp']}&loss=14&angle={p['inclination']}&aspect={p['azimuth']-180}&outputformat=json")
    df_pv = pd.DataFrame(requests.get(pvgis_url).json()['outputs']['hourly'])
    
    # 2. Tratamento Inicial
    df_pv['mes'] = df_pv['time'].str[4:6].astype(int)
    df_pv['dia'] = df_pv['time'].str[6:8].astype(int)
    df_pv['hora'] = df_pv['time'].str[9:11].astype(int)
    df_pv['prod_dc'] = df_pv['P'] / 1000
    df_pv = df_pv[~((df_pv['mes'] == 2) & (df_pv['dia'] == 29))]
    
    df_merged = pd.merge(df_cons, df_pv, on=['mes', 'dia', 'hora'])
    df_merged['cons_kwh'] = df_merged['Peso_Horario_Mil'] * p['consumo_anual']

    # 3. Simulação de Bateria (Iteração Horária)
    soc = 0.0  # Estado de carga inicial (0 kWh)
    cap_max = p['cap_bat']
    list_auto, list_import, list_exced, list_soc = [], [], [], []

    for _, row in df_merged.iterrows():
        prod = min(row['prod_dc'], p['p_ac']) # Produção limitada pelo inversor
        cons = row['cons_kwh']
        
        # Prioridade 1: Autoconsumo Direto
        auto_dir = min(prod, cons)
        net_energy = prod - cons
        
        if net_energy > 0: # Excesso: Carrega Bateria
            can_charge = cap_max - soc
            charge = min(net_energy, can_charge)
            soc += charge
            excedente = net_energy - charge
            importacao = 0
        else: # Défice: Descarrega Bateria
            needed = abs(net_energy)
            discharge = min(needed, soc)
            soc -= discharge
            importacao = needed - discharge
            excedente = 0
            
        list_auto.append(auto_dir + (discharge if net_energy < 0 else 0))
        list_import.append(importacao)
        list_exced.append(excedente)
        list_soc.append(soc)

    df_merged['autoconsumo_kwh'] = list_auto
    df_merged['importacao_kwh'] = list_import
    df_merged['excedente_kwh'] = list_exced
    df_merged['soc_kwh'] = list_soc

    # 4. Agregação
    resumo = df_merged.groupby('mes').agg({'prod_dc': 'sum', 'cons_kwh': 'sum', 'autoconsumo_kwh': 'sum', 
                                           'importacao_kwh': 'sum', 'excedente_kwh': 'sum'}).reset_index()
    return resumo, df_merged

st.set_page_config(page_title="Simulador SOLENERGE", layout="wide")
run, params = render_sidebar()
if run:
    resumo, horario = executar_simulacao(params)
    render_dashboard(resumo, horario, params)
