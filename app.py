import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_js_eval import get_geolocation
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Tesis Café - Persistente", layout="centered")

# URL de tu Google Sheet (Copia la tuya aquí)
# IMPORTANTE: La hoja debe tener permisos de EDICIÓN para "Cualquier persona con el enlace"
SHEET_URL = "https://docs.google.com/spreadsheets/d/TU_ID_DE_HOJA_AQUÍ/edit?usp=sharing"

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- CSS DE ALTA VISIBILIDAD ---
st.markdown("""
    <style>
    .stApp { background-color: #F4F1EE !important; }
    h1, h2, h3, label, p, span { color: #2D1B08 !important; }
    .stButton>button { width: 100%; border-radius: 12px; height: 4em; background-color: #5D4037 !important; color: white !important; font-weight: bold; }
    .stExpander { background-color: #FFFFFF !important; border: 1px solid #D7CCC8 !important; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

st.title("☕ Recolección Permanente")
st.caption("Los datos se guardan automáticamente en la nube (Google Sheets)")

# --- LÓGICA DE CAPTURA ---
with st.expander("⚖️ Consentimiento", expanded=False):
    consentimiento = st.checkbox("Acepto participar")

if consentimiento:
    # GPS
    if st.button("🌐 CAPTURAR GPS"):
        loc = get_geolocation()
        if loc:
            st.session_state['gps'] = f"{loc['coords']['latitude']}, {loc['coords']['longitude']}"
            st.success("Ubicación fijada")
    
    coords = st.text_input("Coordenadas", value=st.session_state.get('gps', ""))

    with st.form("encuesta_permanente", clear_on_submit=True):
        finca = st.text_input("Finca / Productor *")
        muni = st.selectbox("Municipio", ["Vélez", "Guavatá", "Jesús María", "Chipatá", "La Belleza"])
        hec = st.number_input("Hectáreas", 0.0, 100.0, 1.0)
        
        st.markdown("**Tecnología y Proceso**")
        maq = st.selectbox("Despulpado", ["Manual", "Motor", "Ecológico"])
        ferm = st.selectbox("Fermentación", ["Tradicional", "Sumergida", "Anaeróbica"])
        sec = st.selectbox("Secado", ["Patio", "Marquesina", "Silo"])
        amb = st.radio("Ambiental", ["Sin tratamiento", "Pozo Séptico", "Filtro Verde"])
        
        enviar = st.form_submit_button("💾 GUARDAR PERMANENTE")

    if enviar:
        if not finca:
            st.error("Falta el nombre de la finca")
        else:
            try:
                # 1. Leer datos actuales de la nube
                existing_data = conn.read(spreadsheet=SHEET_URL, usecols=list(range(13)))
                
                # 2. Crear nueva fila
                nuevo_registro = pd.DataFrame([{
                    "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Finca": finca,
                    "Municipio": muni,
                    "Coordenadas": coords,
                    "Hectareas": hec,
                    "Tec_Despulpado": maq,
                    "Edad_Maq": 0, # Puedes agregar el input si lo deseas
                    "Fermentacion": ferm,
                    "Lavado": "N/A",
                    "Secado": sec,
                    "Control_Hum": "N/A",
                    "Manejo_Pulpa": "N/A",
                    "Ambiental": amb
                }])
                
                # 3. Concatenar y actualizar
                updated_df = pd.concat([existing_data, nuevo_registro], ignore_index=True)
                conn.update(spreadsheet=SHEET_URL, data=updated_df)
                
                st.success("✅ ¡Datos enviados a Google Sheets!")
                st.balloons()
            except Exception as e:
                st.error(f"Error al guardar: {e}")
                st.info("Asegúrate de que la hoja de Google sea pública para edición.")

# --- BOTÓN DE RESPALDO LOCAL ---
st.divider()
st.subheader("📊 Consulta de Avance")
if st.button("🔄 Ver datos actuales en la nube"):
    df_cloud = conn.read(spreadsheet=SHEET_URL)
    st.dataframe(df_cloud)
