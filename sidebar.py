import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.header("⚙️ Configuração Técnica")
        
        # Conforme o relatório (Perfil A para indústria)
        perfil_tipo = st.selectbox("Perfil de Consumo (ERSE)", ["A", "B", "C"], index=0)
        
        st.subheader("🔌 Inversor e Bateria")
        inversores_dict = {
            "3 kW": 3, "5 kW": 5, "10 kW": 10, "20 kW": 20, "50 kW": 50, "100 kW": 100
        }
        inv_choice = st.selectbox("Inversor Nominal (AC)", list(inversores_dict.keys()), index=5)
        p_ac_total = inversores_dict[inv_choice]
        
        # Capacidade de Armazenamento [Ref: Relatório SOLENERGE 100 kWh]
        cap_bateria = st.number_input("Capacidade Bateria (kWh)", min_value=0.0, value=100.0, step=5.0)
        
        st.subheader("☀️ Painéis Fotovoltaicos")
        n_modulos = st.number_input("Nº Módulos", min_value=1, value=180)
        p_wp = st.number_input("Wp Unitário", value=590)
        
        p_dc_total = (n_modulos * p_wp) / 1000 
        racio = p_dc_total / p_ac_total 
        
        st.metric("Rácio DC/AC", f"{racio:.2f}")
        # Recomendação técnica para Açores (Compensação de radiação difusa)
        if 1.3 <= racio <= 1.4:
            st.success("Rácio Otimizado para os Açores (1.3-1.4)")
        
        with st.expander("Geometria e Custos"):
            lat = st.number_input("Latitude", value=37.82) 
            lon = st.number_input("Longitude", value=-25.82)
            inclination = st.slider("Inclinação (°)", 0, 90, 15)
            azimuth = st.slider("Azimute (°)", 0, 360, 180)
            consumo_anual = st.number_input("Consumo Anual (kWh)", value=143254)
            preco_compra = st.number_input("Compra (€/kWh)", value=0.183)
            preco_venda = st.number_input("Venda (€/kWh)", value=0.04)

        run_sim = st.button("🚀 Executar Simulação", type="primary", use_container_width=True)
        
        return run_sim, {
            "perfil": perfil_tipo, "lat": lat, "lon": lon, "kwp": p_dc_total,
            "p_ac": p_ac_total, "cap_bat": cap_bateria, "inclination": inclination,
            "azimuth": azimuth, "consumo_anual": consumo_anual,
            "preco_compra": preco_compra, "preco_venda": preco_venda
        }
