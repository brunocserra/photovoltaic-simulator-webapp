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
    
    try:
        res = requests.get(urls[p['perfil']])
        df_cons = pd.read_csv(io.StringIO(res.text))
        
        # Configuração original do PVGIS
        pvgis_url = (f"https://re.jrc.ec.europa.eu/api/v5_2/seriescalc?lat={p['lat']}&lon={p['lon']}"
                     f"&peakpower={p['kwp']}&loss=14&mountingplace=free&angle={p['inclination']}"
                     f"&aspect={p['azimuth']-180}&pvcalculation=1&outputformat=json")
        
        req_pvgis = requests.get(pvgis_url)
        data = req_pvgis.json()
        df_pv = pd.DataFrame(data['outputs']['hourly'])
        
        df_pv['mes'] = df_pv['time'].str[4:6].astype(int)
        df_pv['dia'] = df_pv['time'].str[6:8].astype(int)
        df_pv['hora'] = df_pv['time'].str[9:11].astype(int)
        df_pv['prod_dc'] = df_pv['P'] / 1000
        df_pv = df_pv[~((df_pv['mes'] == 2) & (df_pv['dia'] == 29))]
        
        df_merged = pd.merge(df_cons, df_pv, on=['mes', 'dia', 'hora'])
        df_merged['cons_kwh'] = df_merged['Peso_Horario_Mil'] * p['consumo_anual']

        # Simulação de Bateria
        soc = 0.0
        cap_max = p['cap_bat']
        l_auto, l_imp, l_exc, l_soc, l_prod_ac = [], [], [], [], []

        for _, row in df_merged.iterrows():
            prod_ac_potencial = min(row['prod_dc'], p['p_ac']) 
            cons = row['cons_kwh']
            
            auto_direto = min(prod_ac_potencial, cons)
            net_energy = prod_ac_potencial - cons
            
            if net_energy > 0: 
                charge = min(net_energy, cap_max - soc)
                soc += charge
                excedente = net_energy - charge
                importacao = 0
                auto_total = auto_direto
            else: 
                needed = abs(net_energy)
                discharge = min(needed, soc)
                soc -= discharge
                importacao = needed - discharge
                excedente = 0
                auto_total = auto_direto + discharge
                
            l_auto.append(auto_total)
            l_imp.append(importacao)
            l_exc.append(excedente)
            l_soc.append(soc)
            l_prod_ac.append(prod_ac_potencial)

        df_merged['autoconsumo_kwh'] = l_auto
        df_merged['importacao_kwh'] = l_imp
        df_merged['excedente_kwh'] = l_exc
        df_merged['soc_kwh'] = l_soc
        df_merged['prod_ac_kwh'] = l_prod_ac

        resumo = df_merged.groupby('mes').agg({
            'prod_dc': 'sum', 'prod_ac_kwh': 'sum', 'cons_kwh': 'sum', 
            'autoconsumo_kwh': 'sum', 'importacao_kwh': 'sum', 'excedente_kwh': 'sum'
        }).reset_index()
        
        return resumo, df_merged
    except Exception as e:
        st.error(f"Erro na simulação: {e}")
        return None, None

st.set_page_config(page_title="PV Sim Azores Pro", layout="wide")
run, params = render_sidebar()
if run:
    with st.spinner("Simulando..."):
        res_m, df_h = executar_simulacao(params)
        if res_m is not None:
            render_dashboard(res_m, df_h, params)
