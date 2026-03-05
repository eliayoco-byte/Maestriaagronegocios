import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_js_eval import get_geolocation

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Tesis Café - Vélez", page_icon="☕", layout="centered")

# --- CSS ROBUSTO (Anti-Modo Noche y optimizado para sol de campo) ---
st.markdown("""
    <style>
    /* Forzar fondo claro y texto oscuro para legibilidad total */
    .stApp { background-color: #F4F1EE !important; }
    h1, h2, h3, h4, p, label, span { color: #2D1B08 !important; font-family: 'sans-serif'; }
    
    /* Estilo de los Expanders (Secciones colapsables) */
    .stExpander {
        background-color: #FFFFFF !important;
        border: 1px solid #D7CCC8 !important;
        border-radius: 12px !important;
        margin-bottom: 10px !important;
    }
    
    /* Botones Grandes para el pulgar en celular */
    .stButton>button {
        width: 100% !important;
        border-radius: 12px !important;
        height: 4em !important;
        background-color: #5D4037 !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }
    
    /* Inputs y Selectores */
    .stTextInput>div>div>input, .stSelectbox>div>div, .stNumberInput>div>div>input {
        background-color: #FFFFFF !important;
        color: #2D1B08 !important;
        border: 1px solid #D7CCC8 !important;
    }

    /* Ajuste para Radio Buttons en móvil */
    .stRadio > div {
        background-color: #FFFFFF !important;
        padding: 15px !important;
        border-radius: 10px !important;
        border: 1px solid #E0E0E0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAR BASE DE DATOS ---
if 'db_tesis' not in st.session_state:
    st.session_state['db_tesis'] = pd.DataFrame()

# --- TÍTULO ---
st.title("☕ Caracterización Técnica")
st.caption("Instrumento de Investigación - Tesis de Maestría")

# --- MENÚ DE NAVEGACIÓN ---
menu = st.tabs(["📝 Recolección", "📊 Datos Guardados"])

with menu[0]:
    # Consentimiento Ético
    with st.expander("⚖️ Consentimiento Informado", expanded=True):
        st.write("Acepto que los datos recolectados se utilicen para fines académicos de tesis.")
        consentimiento = st.checkbox("Acepto participar")

    if consentimiento:
        # GEOPOSICIÓN
        st.subheader("📍 Geolocalización")
        if st.button("🌐 CAPTURAR UBICACIÓN GPS"):
            loc = get_geolocation()
            if loc:
                lat = loc['coords']['latitude']
                lon = loc['coords']['longitude']
                st.session_state['temp_gps'] = f"{lat}, {lon}"
                st.success(f"Ubicación: {lat}, {lon}")
            else:
                st.error("Error: Activa el GPS y da permisos al navegador.")
        
        coords = st.text_input("Coordenadas actuales", value=st.session_state.get('temp_gps', ""), placeholder="Pulsa el botón de arriba...")

        # FORMULARIO DE CARACTERIZACIÓN
        with st.form("encuesta_tesis", clear_on_submit=True):
            
            with st.expander("👤 1. IDENTIFICACIÓN", expanded=True):
                finca = st.text_input("Nombre de la Finca / Productor *")
                municipio = st.selectbox("Municipio", ["Vélez", "Guavatá", "Jesús María", "Chipatá", "La Belleza", "Florián", "Bolívar", "Albania", "Puente Nacional"])
                hectareas = st.number_input("Hectáreas totales en café", 0.0, 500.0, 1.0)

            with st.expander("⚙️ 2. MAQUINARIA Y PROCESO"):
                tipo_maq = st.selectbox("Tecnología de Despulpado", ["Manual", "Motor Tradicional", "Módulo Ecológico (BECO)"])
                edad_maq = st.number_input("Antigüedad de la Maquina (Años)", 0, 80, 5)
                metodo_ferm = st.selectbox("Método de Fermentación", ["Seco Tradicional", "Tanque Sumergido", "Anaeróbico (Bolsas/Tanque sellado)"])
                lavado = st.selectbox("Técnica de Lavado", ["Canal de Correteo", "En Tanque", "Lavadora Mecánica"])

            with st.expander("☀️ 3. SECADO Y CALIDAD"):
                tipo_secado = st.selectbox("Sistema de Secado", ["Patio/Suelo", "Marquesina/Parabólico", "Silo (Mecánico)", "Zarandas"])
                control_hum = st.radio("Control de Humedad", ["Al tacto/Oído", "Medidor Digital", "No realiza"])

            with st.expander("🌳 4. GESTIÓN AMBIENTAL"):
                manejo_pulpa = st.selectbox("Manejo de Pulpa", ["Botadero Abierto", "Abono Simple", "Lombricultura/Compostaje"])
                manejo_aguas = st.radio("Tratamiento de Aguas Mieles", ["Sin tratamiento", "Pozo Séptico", "Sistema de Filtros/SMTA"])

            st.divider()
            enviar = st.form_submit_button("📥 GUARDAR EN MI BASE DE DATOS")

        if enviar:
            if not finca:
                st.error("⚠️ El nombre de la finca es obligatorio.")
            else:
                nuevo_registro = {
                    "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Finca": finca, "Municipio": municipio, "Coordenadas": coords,
                    "Hectareas": hectareas, "Tec_Despulpado": tipo_maq, "Edad_Maq": edad_maq,
                    "Fermentacion": metodo_ferm, "Lavado": lavado, "Secado": tipo_secado,
                    "Control_Hum": control_hum, "Manejo_Pulpa": manejo_pulpa, "Ambiental": manejo_aguas
                }
                st.session_state['db_tesis'] = pd.concat([st.session_state['db_tesis'], pd.DataFrame([nuevo_registro])], ignore_index=True)
                st.success(f"✅ ¡Registro de '{finca}' guardado!")
                st.balloons()

with menu[1]:
    st.subheader("📊 Datos Acumulados")
    if not st.session_state['db_tesis'].empty:
        df = st.session_state['db_tesis']
        st.write(f"Total registros: **{len(df)}**")
        st.dataframe(df, use_container_width=True)
        
        st.divider()
        
        # --- BOTÓN DE DESCARGA (CORREGIDO) ---
        csv = df.to_csv(index=False, sep=";").encode('utf-8-sig')
        
        st.download_button(
            label="📥 DESCARGAR BASE DE DATOS (EXCEL/CSV)",
            data=csv,
            file_name=f"Datos_Tesis_Maestria_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        if st.button("🗑️ Borrar Todo (Reiniciar Sesión)"):
            st.session_state['db_tesis'] = pd.DataFrame()
            st.rerun()
    else:
        st.info("Aún no tienes datos guardados en esta sesión.")

st.divider()
st.caption("Herramienta de Investigación - Facultad de Ciencias Agrarias")
