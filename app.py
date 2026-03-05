import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from streamlit_js_eval import get_geolocation

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="Tesis Maestría - Café", layout="centered")

# --- DISEÑO PROFESIONAL (Resistente a Modo Noche) ---
st.markdown("""
    <style>
    /* Estilo para las tarjetas de cada sección */
    .stColumn > div {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        margin-bottom: 20px;
    }
    /* Botón de guardado estilo institucional */
    .stButton>button {
        width: 100%;
        border-radius: 25px;
        height: 3.5em;
        background-color: #4E342E !important;
        color: white !important;
        font-weight: bold;
        border: none;
    }
    /* Títulos de sección */
    .section-head {
        color: #795548;
        font-size: 1.2em;
        font-weight: bold;
        border-left: 5px solid #795548;
        padding-left: 10px;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN DE DATOS ---
if 'db' not in st.session_state:
    st.session_state['db'] = pd.DataFrame()

# --- TÍTULO ---
st.title("🔬 Caracterización Técnica de Beneficiaderos")
st.caption("Instrumento de Recolección de Datos Primarios - Provincia de Vélez")

# --- PESTAÑAS ---
tab1, tab2 = st.tabs(["📋 Instrumento de Campo", "📊 Análisis y Exportación"])

with tab1:
    # 1. GEOPOSICIONAMIENTO
    st.markdown('<p class="section-head">📍 Localización y GPS</p>', unsafe_allow_html=True)
    col_gps1, col_gps2 = st.columns([1,1])
    with col_gps1:
        if st.button("🌐 Obtener GPS Actual"):
            loc = get_geolocation()
            if loc:
                st.session_state['lat_lon'] = f"{loc['coords']['latitude']}, {loc['coords']['longitude']}"
                st.success("Coordenadas fijadas")
    with col_gps2:
        coords = st.text_input("Coordenadas", value=st.session_state.get('lat_lon', ""), placeholder="Esperando señal...")

    # FORMULARIO DE TESIS
    with st.form("form_tesis"):
        
        # DIMENSIÓN 1: DATOS DEL PRODUCTOR
        st.markdown('<p class="section-head">👤 Dimensión 1: Contexto Productivo</p>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        finca = c1.text_input("ID / Nombre Finca *")
        municipio = c2.selectbox("Municipio", ["Vélez", "Guavatá", "Jesús María", "Chipatá", "La Belleza", "Florián", "Bolívar", "Albania", "Puente Nacional"])
        
        c3, c4 = st.columns(2)
        hectareas = c3.number_input("Hectáreas totales café", 0.1, 100.0, 1.0)
        certificacion = c4.selectbox("Certificación Actual", ["Ninguna", "4C", "Rainforest", "Fairtrade", "Orgánico"])

        # DIMENSIÓN 2: INFRAESTRUCTURA Y MAQUINARIA
        st.markdown('<p class="section-head">⚙️ Dimensión 2: Caracterización de Maquinaria</p>', unsafe_allow_html=True)
        tipo_despulpador = st.selectbox("Tecnología de Despulpado", 
            ["Pechero Tradicional (Manual/Motor)", "Cilindro Horizontal", "Módulo Ecológico Despulpado en Seco", "Módulo Compacto (BECO)"])
        
        c5, c6 = st.columns(2)
        potencia = c5.selectbox("Fuente de Energía", ["Manual", "Motor Eléctrico < 1HP", "Motor Eléctrico > 1HP", "Motor Gasolina"])
        antiguedad = c6.number_input("Edad del equipo (Años)", 0, 50, 5)
        
        mantenimiento = st.select_slider("Frecuencia de Mantenimiento / Calibración", 
            options=["Nunca", "Cada Cosecha", "Cada Pase", "Preventivo Programado"])

        # DIMENSIÓN 3: PROCESAMIENTO Y AGUA
        st.markdown('<p class="section-head">🧪 Dimensión 3: Dinámica de Procesos</p>', unsafe_allow_html=True)
        c7, c8 = st.columns(2)
        tiempo_ferm = c7.slider("Tiempo Fermentación (Horas)", 6, 72, 18)
        control_punto = c8.selectbox("Control de Fermentación", ["Empírico (Tacto)", "Fermaestro", "Sensor de pH", "Cronometrado"])
        
        consumo_agua = st.selectbox("Uso de agua en el proceso", 
            ["Alto (Canal de correteo)", "Medio (Lavado en tanque)", "Bajo (Lavadora mecánica)", "Nulo (Beneficio Natural/Honey)"])

        # DIMENSIÓN 4: SECADO Y CONSERVACIÓN
        st.markdown('<p class="section-head">☀️ Dimensión 4: Secado y Calidad</p>', unsafe_allow_html=True)
        c9, c10 = st.columns(2)
        tec_secado = c9.selectbox("Tecnología de Secado", ["Suelo/Patio", "Marquesina Tradicional", "Marquesina Ventilada (Zarandas)", "Silo Mecánico"])
        tiempo_secado = c10.number_input("Días promedio de secado", 1, 15, 5)
        
        control_humedad = st.radio("¿Mide humedad final?", ["No realiza (Al tacto)", "Sí, con determinador manual", "Sí, con medidor digital (10-12%)"], horizontal=True)

        # DIMENSIÓN 5: GESTIÓN AMBIENTAL
        st.markdown('<p class="section-head">🌱 Dimensión 5: Sostenibilidad</p>', unsafe_allow_html=True)
        tratamiento_aguas = st.selectbox("Manejo de Aguas Mieles", 
            ["Vertimiento Directo", "Pozo Séptico", "Sistema de Filtros Verdes", "SMTA (Sistema de Tratamiento Modular)"])
        manejo_pulpa = st.selectbox("Manejo de Pulpa de Café", ["Sin tratamiento", "Compostaje Simple", "Lombricultura", "Uso como Biomasa"])

        # BOTÓN DE GUARDADO
        st.divider()
        submit = st.form_submit_button("📥 REGISTRAR CARACTERIZACIÓN COMPLETA")

    if submit:
        if not finca:
            st.error("El nombre de la finca es obligatorio para el registro de la tesis.")
        else:
            # Crear diccionario de datos (Puntajes para análisis posterior)
            nuevo_dato = {
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Finca": finca, "Municipio": municipio, "Coordenadas": coords,
                "Hectareas": hectareas, "Certificacion": certificacion,
                "Tec_Despulpado": tipo_despulpador, "Energia": potencia,
                "Edad_Maq": antiguedad, "Mantenimiento": mantenimiento,
                "Horas_Ferm": tiempo_ferm, "Control_Ferm": control_punto,
                "Uso_Agua": consumo_agua, "Tec_Secado": tec_secado,
                "Dias_Secado": tiempo_secado, "Control_Humedad": control_humedad,
                "Tratamiento_Aguas": tratamiento_aguas, "Manejo_Pulpa": manejo_pulpa
            }
            
            st.session_state['db'] = pd.concat([st.session_state['db'], pd.DataFrame([nuevo_dato])], ignore_index=True)
            st.success("✅ Registro guardado en la memoria local.")
            st.balloons()

with tab2:
    if not st.session_state['db'].empty:
        df = st.session_state['db']
        st.subheader("📊 Avance de la Investigación")
        st.metric("Fincas Caracterizadas", len(df))
        
        # Gráfico de rigor para la tesis: Distribución por Tecnología
        fig = go.Figure(data=[go.Pie(labels=df['Tec_Despulpado'].value_counts().index, 
                                   values=df['Tec_Despulpado'].value_counts().values, hole=.3)])
        fig.update_layout(title_text="Distribución Tecnológica de Despulpado", height=400)
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.dataframe(df, use_container_width=True)
        
        # DESCARGA
        csv = df.to_csv(index=False, sep=";").encode('utf-8-sig')
        st.download_button("📥 DESCARGAR BASE DE DATOS (CSV/EXCEL)", csv, 
                           f"Matriz_Datos_Tesis_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
    else:
        st.info("No hay datos registrados todavía.")

# PIE DE PÁGINA PROFESIONAL
st.markdown("---")
st.caption("Instrumento desarrollado para fines de Investigación de Maestría. Todos los derechos reservados.")
