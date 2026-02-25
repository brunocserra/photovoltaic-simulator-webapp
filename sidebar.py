import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.header("⚙️ Configuração Técnica")
        
        # Localização com foco nos Açores/Portugal
        st.subheader("Localização")
        with st.expander("Coordenadas (Lat/Lon)", expanded=False):
            lat = st.number_input("Latitude", value=37.7400, format="%.4f")
            lon = st.number_input("Longitude", value=-25.6700, format="%.4f")
        
        # Parâmetros do Sistema
        st.subheader("Sistema Fotovoltaico")
        kwp = st.number_input("Potência Instalada (kWp)", value=3.0, step=0.5, help="Potência de pico dos painéis.")
        inclination = st.slider("Inclinação (°)", 0, 90, 35)
        azimuth = st.slider("Azimute (°)", 0, 360, 180, help="180º = Sul (Ideal)")
        
        # Parâmetros Económicos e Consumo
        st.header("📊 Gestão de Energia")
        consumo_anual = st.number_input("Consumo Anual Total (kWh)", value=5000, step=100)
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            preco_compra = st.number_input("Compra (€/kWh)", value=0.22, format="%.2f")
        with col_p2:
            preco_venda = st.number_input("Venda (€/kWh)", value=0.04, format="%.2f")
            
        st.markdown("---")
        run_sim = st.button("🚀 Executar Simulação", type="primary", use_container_width=True)
        
        return run_sim, {
            "lat": lat, "lon": lon, "kwp": kwp, 
            "inclination": inclination, "azimuth": azimuth,
            "consumo_anual": consumo_anual, 
            "preco_compra": preco_compra, "preco_venda": preco_venda
        }
