import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from streamlit_js_eval import get_geolocation

# --- CONFIGURACIÓN DE PÁGINA MÓVIL ---
st.set_page_config(page_title="Investigación Café - Vélez", page_icon="☕", layout="centered")

# CSS para optimizar la interfaz en celulares (botones grandes y legibles)
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #4E342E; color: white; font-weight: bold; }
    .stExpander { border: 1px solid #795548; border-radius: 12px; margin-bottom: 8px; background-color: #fdfaf8; }
    .stRadio > div { flex-direction: column; gap: 10px; }
    label { font-size: 1.1em !important; font-weight: bold !important; color: #3E2723; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAR BASE DE DATOS EN SESIÓN ---
if 'db_tesis' not in st.session_state:
    st.session_state['db_tesis'] = pd.DataFrame()

# --- TÍTULO E INTRODUCCIÓN ---
st.title("🔬 Caracterización Técnica de Beneficiaderos")
st.caption("Instrumento de Recolección de Datos Primarios | Tesis de Maestría")

# --- SISTEMA DE NAVEGACIÓN ---
menu = st.tabs(["📝 Formulario de Campo", "📊 Datos Acumulados"])

with menu[0]:
    # 1. CONSENTIMIENTO Y ÉTICA
    with st.expander("⚖️ Consentimiento Informado", expanded=True):
        st.write("Esta encuesta recoge datos para fines de investigación académica. Los datos son confidenciales.")
        consentimiento = st.checkbox("Acepto participar en la investigación")

    if consentimiento:
        # 2. GEOLOCALIZACIÓN (GPS REAL)
        st.subheader("📍 Ubicación Geográfica")
        col_gps, col_ver = st.columns([1, 1])
        
        with col_gps:
            if st.button("🌐 CAPTURAR GPS"):
                loc = get_geolocation()
                if loc:
                    lat = loc['coords']['latitude']
                    lon = loc['coords']['longitude']
                    st.session_state['temp_gps'] = f"{lat}, {lon}"
                    st.success("📍 Ubicación obtenida")
                else:
                    st.warning("Activa el GPS y da permisos al navegador.")
        
        coords = st.text_input("Coordenadas (Lat, Long)", value=st.session_state.get('temp_gps', ""), placeholder="Esperando señal...")

        # 3. FORMULARIO POR DIMENSIONES (EXPANDERS PARA MÓVIL)
        with st.form("encuesta_maestria", clear_on_submit=True):
            
            # DIMENSIÓN A: IDENTIFICACIÓN
            with st.expander("👤 A. IDENTIFICACIÓN Y ENTORNO", expanded=True):
                finca = st.text_input("Nombre de la Finca / Productor *")
                municipio = st.selectbox("Municipio", ["Vélez", "Guavatá", "Jesús María", "Chipatá", "La Belleza", "Florián", "Bolívar", "Albania", "Puente Nacional"])
                vereda = st.text_input("Vereda")
                hectareas = st.number_input("Hectáreas en Café", min_value=0.0, step=0.1)
                variedades = st.multiselect("Variedades instaladas", ["Castillo", "Cenicafé 1", "Colombia", "Típica", "Tabi", "Borbón", "Caturra"])

            # DIMENSIÓN B: INFRAESTRUCTURA DE RECEPCIÓN
            with st.expander("🏗️ B. INFRAESTRUCTURA DE RECEPCIÓN"):
                material_tolva = st.radio("Material de Tolvas/Tanques:", 
                    ["Madera / Tierra / Ladrillo rústico", "Cemento enchapado / Cerámica", "Acero Inoxidable / Epóxico"])
                estado_higiene = st.select_slider("Estado de higiene del beneficiadero:", options=["Crítico", "Aceptable", "Excelente"])

            # DIMENSIÓN C: PROCESO DE DESPULPADO (MECÁNICO)
            with st.expander("⚙️ C. CARACTERIZACIÓN DESPULPADO"):
                tipo_maq = st.selectbox("Tecnología de Despulpado:", ["Pechero Manual", "Despulpador de Pechero Eléctrico", "Cilindro Horizontal", "Módulo Ecológico (BECO / Compacto)"])
                antiguedad = st.number_input("Años de antigüedad de la maquinaria:", 0, 50, 5)
                calibracion = st.radio("¿Realiza calibración antes de cosecha?", ["Nunca", "Ocasionalmente", "Siempre (Antes de cada pase)"])
                presencia_grano = st.radio("Presencia de grano en la pulpa:", ["Abundante", "Moderada", "Nula / Mínima"])

            # DIMENSIÓN D: FERMENTACIÓN Y LAVADO
            with st.expander("🧪 D. FERMENTACIÓN Y LAVADO"):
                metodo_ferm = st.selectbox("Método de Fermentación:", ["Tanque tradicional seco", "Fermentación sumergida", "Tanque con control térmico", "Bolsas (Anaeróbico)"])
                punto_ferm = st.radio("Determinación del punto de lavado:", ["Empírico (Tacto/Olor/Palo)", "Tiempo fijo (Horas)", "Instrumentado (Fermaestro / pH-metro)"])
                lavado = st.selectbox("Técnica de Lavado:", ["Canal de correteo", "Lavado en tanque (3 cambios)", "Lavadora mecánica / Bomba"])

            # DIMENSIÓN E: SECADO Y CALIDAD
            with st.expander("☀️ E. SECADO Y CONSERVACIÓN"):
                tipo_secado = st.selectbox("Tipo de Secado Principal:", ["Patio de cemento / El suelo", "Eldas / Carros", "Marquesina / Casa Elva", "Silo (Mecánico)"])
                control_hum = st.radio("Control de Humedad Final:", ["Visual / Morder el grano", "Medidor de Humedad Digital", "No realiza control"])

            # DIMENSIÓN F: GESTIÓN AMBIENTAL
            with st.expander("🌳 F. GESTIÓN DE RESIDUOS"):
                manejo_pulpa = st.selectbox("Manejo de la Pulpa:", ["Botadero abierto", "Abono orgánico / Compostaje", "Lombricultura", "Venta/Uso energético"])
                manejo_aguas = st.radio("Tratamiento Aguas Mieles:", ["Vertimiento directo a quebrada", "Pozo séptico", "Sistemas SMTA / Filtros verdes"])

            # BOTÓN FINAL
            submit = st.form_submit_button("📥 REGISTRAR INFORMACIÓN")

        if submit:
            if not finca:
                st.error("⚠️ El nombre de la finca es obligatorio.")
            else:
                # CREAR REGISTRO PARA LA TESIS
                nuevo_registro = {
                    "Fecha_Captura": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Finca": finca,
                    "Municipio": municipio,
                    "Vereda": vereda,
                    "Coordenadas": coords,
                    "Hectareas": hectareas,
                    "Variedades": ", ".join(variedades),
                    "Material_Tolva": material_tolva,
                    "Higiene": estado_higiene,
                    "Tec_Despulpado": tipo_maq,
                    "Edad_Maq": antiguedad,
                    "Calibracion": calibracion,
                    "Grano_en_Pulpa": presencia_grano,
                    "Metodo_Ferm": metodo_ferm,
                    "Control_Ferm": punto_ferm,
                    "Tec_Lavado": lavado,
                    "Tipo_Secado": tipo_secado,
                    "Control_Hum": control_hum,
                    "Manejo_Pulpa": manejo_pulpa,
                    "Manejo_Aguas": manejo_aguas
                }
                
                # GUARDAR
                st.session_state['db_tesis'] = pd.concat([st.session_state['db_tesis'], pd.DataFrame([nuevo_registro])], ignore_index=True)
                st.success(f"✅ Datos de la finca '{finca}' guardados con éxito.")
                st.balloons()
    else:
        st.info("Debe aceptar el consentimiento informado para iniciar la recolección.")

with menu[1]:
    st.subheader("📊 Base de Datos de la Tesis")
    
    if not st.session_state['db_tesis'].empty:
        df = st.session_state['db_tesis']
        
        # Resumen rápido
        st.write(f"Total registros capturados: **{len(df)}**")
        st.dataframe(df, use_container_width=True)
        
        st.divider()
        
        # EXPORTACIÓN
        st.subheader("📥 Exportar para Análisis")
        st.write("Descarga este archivo para abrirlo en Excel, SPSS o R.")
        
        # Generamos CSV con codificación para Excel
        csv = df.to_csv(index=False, sep=";").encode('utf-8-sig')
        
        st.download_button(
            label="Descargar CSV para Excel",
            data=csv,
            file_name=f"Tesis_Cafe_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
        
        if st.button("🗑️ Borrar sesión actual"):
            st.session_state['db_tesis'] = pd.DataFrame()
            st.rerun()
    else:
        st.info("No hay datos capturados en esta sesión todavía.")

# PIE DE PÁGINA
st.markdown("---")
st.caption("Investigación desarrollada por el autor para optar al título de Magíster.")
