import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="MATO - Café", page_icon="☕", layout="centered")

# --- INICIALIZAR MEMORIA TEMPORAL ---
# Esto guarda los datos en la sesión actual mientras no cierres la pestaña
if 'datos_recolectados' not in st.session_state:
    st.session_state['datos_recolectados'] = pd.DataFrame(columns=[
        "Fecha", "Finca", "Municipio", "Volumen_Pico_Kg", 
        "Tolva_Material", "Despulpado_Tec", "Despulpado_Calibracion",
        "Fermentacion_Control", "Secado_Tec"
    ])

# --- ENCABEZADO ---
st.title("☕ Auditoría MATO")
st.markdown("Herramienta de captura de datos para la evaluación técnico-operativa de beneficiaderos de café en la provincia de Vélez.")

# --- FORMULARIO DE CAPTURA ---
with st.form("formulario_mato", clear_on_submit=True):
    st.subheader("1. Datos Generales")
    col1, col2 = st.columns(2)
    with col1:
        finca = st.text_input("ID / Nombre de la Finca *")
    with col2:
        municipio = st.selectbox("Municipio *", ["Vélez", "Guavatá", "Jesús María"])

    st.subheader("2. Dimensión: Capacidad y Recepción")
    volumen = st.number_input("Volumen pico de recolección (Kg de cereza/día)", min_value=0, step=10)
    tolva = st.selectbox("Materiales de la Tolva/Tanques", [
        "1 - Madera / Tierra (Riesgo alto)",
        "2 - Cemento rústico",
        "3 - Recubrimiento epóxico / Cerámica / Acero"
    ])

    st.subheader("3. Dimensión: Eficiencia Mecánica (Despulpado)")
    despulpado_tec = st.selectbox("Tecnología de Despulpado", [
        "1 - Pechero tradicional",
        "2 - Cilindro dentado",
        "3 - Módulo ecológico (BECO)"
    ])
    despulpado_cal = st.selectbox("Calibración y Desgaste", [
        "1 - Camisa gastada / Descalibrada",
        "2 - Estado aceptable",
        "3 - Óptimo / Reciente"
    ])

    st.subheader("4. Dimensión: Control (Fermentación y Secado)")
    fermentacion = st.selectbox("Método de punto de lavado (Fermentación)", [
        "1 - Empírico (Tacto / Olor / Tiempo fijo)",
        "2 - Instrumentado (Fermaestro / pH-metro)"
    ])
    secado = st.selectbox("Tecnología de Secado", [
        "1 - Patio / Suelo",
        "2 - Marquesina tradicional",
        "3 - Marquesina con ventilación / Zarandas",
        "4 - Silo mecánico"
    ])

    st.markdown("---")
    # Botón de envío del formulario
    submit_button = st.form_submit_button("Guardar Datos de Finca", type="primary")

# --- LÓGICA AL GUARDAR ---
if submit_button:
    if finca.strip() == "":
        st.error("⚠️ El nombre de la finca es obligatorio.")
    else:
        # Extraer solo el número (código) de las respuestas para facilitar el análisis en SPSS/Excel
        nuevo_registro = {
            "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Finca": finca,
            "Municipio": municipio,
            "Volumen_Pico_Kg": volumen,
            "Tolva_Material": int(tolva[0]),
            "Despulpado_Tec": int(despulpado_tec[0]),
            "Despulpado_Calibracion": int(despulpado_cal[0]),
            "Fermentacion_Control": int(fermentacion[0]),
            "Secado_Tec": int(secado[0])
        }
        
        # Añadir al DataFrame en memoria usando pd.concat
        df_nuevo = pd.DataFrame([nuevo_registro])
        st.session_state['datos_recolectados'] = pd.concat([st.session_state['datos_recolectados'], df_nuevo], ignore_index=True)
        st.success(f"✅ ¡Datos de la finca '{finca}' guardados en la sesión temporal!")

# --- VISUALIZACIÓN Y DESCARGA DE DATOS ---
if not st.session_state['datos_recolectados'].empty:
    st.markdown("### 📊 Datos Recolectados en esta Sesión")
    st.dataframe(st.session_state['datos_recolectados'])
    
    # Convertir a CSV
    csv = st.session_state['datos_recolectados'].to_csv(index=False, sep=";").encode('utf-8')
    
    # Botón de descarga
    st.download_button(
        label="📥 Descargar Base de Datos (CSV)",
        data=csv,
        file_name=f"Datos_MATO_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )
    st.info("💡 Recuerda descargar tu CSV antes de cerrar la pestaña o actualizar la página.")
