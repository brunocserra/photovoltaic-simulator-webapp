import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.header("⚙️ Configuração Técnica")
        
        # 1. Escolha do Perfil
        perfil_tipo = st.selectbox("Perfil de Consumo (ERSE)", ["A", "B", "C"], index=2)
        
        # 2. Configuração do Inversor (Baseado na sua lista)
        st.subheader("🔌 Inversor(es)")
        inversores_dict = {
            "3 kW": 3, "4 kW": 4, "5 kW": 5, "6 kW": 6, "8 kW": 8, "10 kW": 10,
            "12 kW": 12, "15 kW": 15, "17 kW": 17, "20 kW": 20, "25 kW": 25, "30 kW": 30,
            "2 x 20 kW": 40, "2 x 25 kW": 50, "2 x 30 kW": 60, "3 x 25 kW": 75,
            "4 x 20 kW": 80, "4 x 25 kW": 100, "4 x 30 kW": 120
        }
        inv_choice = st.selectbox("Configuração de Inversor", list(inversores_dict.keys()))
        p_ac_total = inversores_dict[inv_choice]

        # 3. Configuração de Módulos
        st.subheader("☀️ Painéis Fotovoltaicos")
        col1, col2 = st.columns(2)
        with col1:
            n_modulos = st.number_input("Nº Módulos", min_value=1, value=10)
        with col2:
            p_wp = st.number_input("Wp Unitário", value=590)
        
        p_dc_total = (n_modulos * p_wp) / 1000  # kWp
        racio_dc_ac = p_dc_total / p_ac_total

        # Validação de Rácio DC/AC
        st.metric("Rácio DC/AC", f"{racio_dc_ac:.2f}")
        if racio_dc_ac > 1.5:
            st.error(f"⚠️ Rácio Crítico: {racio_dc_ac:.2f} > 1.50. Reduza o nº de painéis ou aumente o inversor.")
            pode_simular = False
        else:
            st.success("Rácio dentro dos limites técnicos.")
            pode_simular = True

        # 4. Configuração de Strings
        st.subheader("🧵 Configuração de Strings")
        n_strings = st.number_input("Nº de Strings", min_value=1, max_value=8, value=1)
        
        strings_config = []
        soma_paineis = 0
        for i in range(n_strings):
            val = st.number_input(f"Módulos na String {i+1}", min_value=1, value=n_modulos//n_strings)
            strings_config.append(val)
            soma_paineis += val
        
        # Validação de Soma de Strings
        if soma_paineis != n_modulos:
            st.warning(f"Soma das strings ({soma_paineis}) ≠ Total de módulos ({n_modulos})")
            pode_simular = False

        # 5. Outros Parâmetros (Ocultos por defeito para limpeza visual)
        with st.expander("Geometria e Custos"):
            lat = st.number_input("Latitude", value=37.7400, format="%.4f")
            lon = st.number_input("Longitude", value=-25.6700, format="%.4f")
            inclination = st.slider("Inclinação (°)", 0, 90, 35)
            azimuth = st.slider("Azimute (°)", 0, 360, 180)
            consumo_anual = st.number_input("Consumo Anual (kWh)", value=5000)
            preco_compra = st.number_input("Compra (€/kWh)", value=0.22)
            preco_venda = st.number_input("Venda (€/kWh)", value=0.04)

        st.markdown("---")
        btn = st.button("🚀 Executar Simulação", type="primary", use_container_width=True, disabled=not pode_simular)
        
        return btn, {
            "perfil": perfil_tipo, "lat": lat, "lon": lon, "kwp": p_dc_total,
            "inclination": inclination, "azimuth": azimuth, "consumo_anual": consumo_anual,
            "preco_compra": preco_compra, "preco_venda": preco_venda,
            "p_ac": p_ac_total, "racio": racio_dc_ac
        }
