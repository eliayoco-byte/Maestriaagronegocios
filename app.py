import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from streamlit_js_eval import get_geolocation

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Tesis Café - Vélez", page_icon="☕", layout="centered")

# --- CSS ROBUSTO (Anti-Modo Noche y Mobile-First) ---
# Forzamos colores que funcionan bien en cualquier modo y aumentamos legibilidad
st.markdown("""
    <style>
    /* Forzar fondo claro y texto oscuro para legibilidad en campo */
    .stApp {
        background-color: #F4F1EE;
    }
    h1, h2, h3, p, label {
        color: #2D1B08 !important;
    }
    /* Estilo de los Expanders (Secciones) */
    .stExpander {
        background-color: #FFFFFF !important;
        border: 1px solid #D7CCC8 !important;
        border-radius: 12px !important;
        margin-bottom: 10px !important;
    }
    /* Botones Grandes y con Contraste */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.8em;
        background-color: #5D4037 !important;
        color: #FFFFFF !important;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    /* Estilo de inputs */
    .stTextInput>div>div>input, .stSelectbox>div>div {
        background-color: #FFFFFF !important;
        color: #2D1B08 !important;
        border-radius: 8px !important;
    }
    /* Radio buttons más fáciles de tocar */
    .stRadio > div {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #E0E0E0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAR BASE DE DATOS ---
if 'db_tesis' not in st.session_state:
    st.session_state['db_tesis'] = pd.DataFrame()

# --- TÍTULO ---
st.title("🔬 Caracterización Técnica")
st.caption("Instrumento de Investigación Primaria - Tesis de Maestría")

# --- MENÚ ---
menu = st.tabs(["📝 Recolección", "📊 Mi Base de Datos"])

with menu[0]:
    # Consentimiento Ético
    with st.expander("⚖️ Consentimiento Informado", expanded=True):
        st.write("Acepto que los datos recolectados se utilicen exclusivamente para fines académicos de tesis.")
        consentimiento = st.checkbox("Acepto participar")

    if consentimiento:
        # GPS
        st.subheader("📍 Ubicación GPS")
        if st.button("🌐 OBTENER COORDENADAS"):
            loc = get_geolocation()
            if loc:
                lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
                st.session_state['temp_gps'] = f"{lat}, {lon}"
                st.success(f"Capturado: {lat}, {lon}")
            else:
                st.error("Error: Activa el GPS del celular.")
        
        coords = st.text_input("Coordenadas Guardadas", value=st.session_state.get('temp_gps', ""))

        # FORMULARIO
        with st.form("encuesta_tesis", clear_on_submit=True):
            
            with st.expander("👤 1. DATOS GENERALES", expanded=True):
                finca = st.text_input("Finca / Productor *")
                municipio = st.selectbox("Municipio", ["Vélez", "Guavatá", "Jesús María", "Chipatá", "La Belleza", "Florián", "Bolívar", "Albania", "Puente Nacional"])
                hectareas = st.number_input("Hectáreas en Café", 0.0, 100.0, 1.0)

            with st.expander("⚙️ 2. MAQUINARIA Y PROCESO"):
                tipo_maq = st.selectbox("Tecnología Despulpado", ["Manual", "Eléctrica Tradicional", "Módulo Ecológico"])
                edad_maq = st.number_input("Antigüedad Máquina (Años)", 0, 60, 5)
                metodo_ferm = st.selectbox("Fermentación", ["Seco Tradicional", "Sumergido", "Anaeróbico"])

            with st.expander("☀️ 3. SECADO Y AMBIENTE"):
                tipo_secado = st.selectbox("Sistema de Secado", ["Patio/Suelo", "Marquesina", "Silo Mecánico"])
                manejo_aguas = st.radio("Tratamiento Aguas Mieles", ["Ninguno", "Pozo Séptico", "Filtro Verde/SMTA"])

            st.divider()
            enviar = st.form_submit_button("📥 GUARDAR DATOS EN LA MATRIZ")

        if enviar:
            if not finca:
                st.error("⚠️ Falta el nombre de la finca.")
            else:
                nuevo = {
                    "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Finca": finca, "Municipio": municipio, "Coordenadas": coords,
                    "Hectareas": hectareas, "Tecnologia": tipo_maq, "Edad_Maq": edad_maq,
                    "Fermentacion": metodo_ferm, "Secado": tipo_secado, "Ambiental": manejo_aguas
                }
                st.session_state['db_tesis'] = pd.concat([st.session_state['db_tesis'], pd.DataFrame([nuevo])], ignore_index=True)
                st.balloons()
                st.success("¡Registro guardado exitosamente!")

with menu[1]:
    st.subheader("📊 Datos de la Investigación")
    if not st.session_state['db_tesis'].empty:
        df = st.session_state['db_tesis']
        st.write(f"Fincas registradas: **{len(df)}**")
        st.dataframe(df, use_container_width=True)
        
        st.divider()
        csv = df.to_csv(index=False, sep=";").encode('utf-8-sig')
        st.downloa
