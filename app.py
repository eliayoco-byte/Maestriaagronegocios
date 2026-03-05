import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Auditoría MATO Pro", page_icon="☕", layout="wide")

# Estilo profesional
st.markdown("""
    <style>
    .reportview-container { background: #f0f2f6; }
    .stMetric { border: 1px solid #795548; padding: 10px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS EN SESIÓN ---
if 'base_datos' not in st.session_state:
    st.session_state['base_datos'] = pd.DataFrame()

# --- FUNCIÓN DE CÁLCULO DE ÍNDICE DE MADUREZ (IMT) ---
def calcular_puntuacion(respuestas):
    # Definimos pesos por dimensión (Total 100%)
    # 1. Infraestructura (15%), 2. Despulpado (25%), 3. Fermentación (25%), 4. Secado (20%), 5. Ambiental (15%)
    
    d1 = (respuestas['r_tolva'] + respuestas['r_aseo']) / 6 * 100
    d2 = (respuestas['r_tec_des'] + respuestas['r_calib'] + respuestas['r_perdida']) / 9 * 100
    d3 = (respuestas['r_metodo_f'] + respuestas['r_control_f'] + respuestas['r_lavado']) / 9 * 100
    d4 = (respuestas['r_tipo_sec'] + respuestas['r_humedad']) / 6 * 100
    d5 = (respuestas['r_pulpa'] + respuestas['r_aguas_mieles']) / 6 * 100
    
    imt = (d1*0.15) + (d2*0.25) + (d3*0.25) + (d4*0.20) + (d5*0.15)
    return round(imt, 2), round(d1, 1), round(d2, 1), round(d3, 1), round(d4, 1), round(d5, 1)

# --- INTERFAZ ---
st.title("☕ Auditoría Técnica MATO - Nivel Profesional")
st.markdown("### Evaluación Integral de la Eficiencia en Beneficiaderos de Café")

t1, t2 = st.tabs(["📋 Formulario de Auditoría", "📊 Análisis de Resultados"])

with t1:
    with st.form("encuesta_robusta"):
        # SECCIÓN 0: IDENTIFICACIÓN
        col_id1, col_id2, col_id3 = st.columns(3)
        with col_id1:
            finca = st.text_input("📍 Nombre de la Finca / Productor")
        with col_id2:
            municipio = st.selectbox("Municipio", ["Vélez", "Guavatá", "Jesús María", "Chipatá", "La Belleza", "Florián"])
        with col_id3:
            altura = st.number_input("⛰️ Altitud (msnm)", min_value=500, max_value=2500, value=1500)

        st.divider()

        # DIMENSIÓN 1: INFRAESTRUCTURA Y RECEPCIÓN (15%)
        st.subheader("1. Infraestructura y Recepción")
        c1, c2 = st.columns(2)
        with c1:
            r_tolva = st.select_slider("Calidad de Tolvas/Tanques", options=[1, 2, 3], 
                                     help="1: Madera/Tierra, 2: Cemento rústico, 3: Acero/Epóxico/Cerámica")
        with c2:
            r_aseo = st.select_slider("Protocolos de Higiene", options=[1, 2, 3],
                                     help="1: Sin limpieza regular, 2: Limpieza básica, 3: Desinfección programada")

        # DIMENSIÓN 2: EFICIENCIA EN DESPULPADO (25%)
        st.subheader("2. Dimensión de Despulpado")
        c3, c4, c5 = st.columns(3)
        with c3:
            r_tec_des = st.selectbox("Tecnología", [1, 2, 3], format_func=lambda x: ["Pechero Tradicional", "Cilindro Horizontal", "Módulo Ecológico (BECO)"][x-1])
        with c4:
            r_calib = st.selectbox("Estado de Calibración", [1, 2, 3], format_func=lambda x: ["Descalibrada (Pasa cereza/grano)", "Aceptable", "Óptima (Sin granos heridos)"][x-1])
        with c5:
            r_perdida = st.selectbox("Pérdida de Grano en Pulpa", [1, 2, 3], format_func=lambda x: ["Alta (>2%)", "Moderada", "Mínima (<0.5%)"][x-1])

        # DIMENSIÓN 3: CONTROL DE FERMENTACIÓN (25%)
        st.subheader("3. Fermentación y Lavado")
        c6, c7, c8 = st.columns(3)
        with c6:
            r_metodo_f = st.selectbox("Tipo de Tanque", [1, 2, 3], format_func=lambda x: ["Tanque rectangular (difícil lavado)", "Circular / Cónico", "Tina de acero / Plástica"][x-1])
        with c7:
            r_control_f = st.selectbox("Control de Punto", [1, 2, 3], format_func=lambda x: ["Visual / Tacto", "Fermaestro / Tiempo controlado", "Sensores pH / Temperatura"][x-1])
        with c8:
            r_lavado = st.selectbox("Uso de Agua en Lavado", [1, 2, 3], format_func=lambda x: ["Canal de correteo (Alto consumo)", "Lavado en tanque", "Lavadora mecánica / Bajo consumo"][x-1])

        # DIMENSIÓN 4: SECADO Y CONSERVACIÓN (20%)
        st.subheader("4. Secado y Almacenamiento")
        c9, c10 = st.columns(2)
        with c9:
            r_tipo_sec = st.selectbox("Sistema de Secado", [1, 2, 3], format_func=lambda x: ["Patios al aire libre", "Marquesina tradicional", "Silo / Zarandas con aire forzado"][x-1])
        with c10:
            r_humedad = st.selectbox("Control de Humedad Final", [1, 2, 3], format_func=lambda x: ["Al tanteo (morder el grano)", "Determinador manual", "Medidor digital (10-12%)"][x-1])

        # DIMENSIÓN 5: GESTIÓN AMBIENTAL (15%)
        st.subheader("5. Impacto Ambiental")
        c11, c12 = st.columns(2)
        with c11:
            r_pulpa = st.selectbox("Manejo de Pulpa", [1, 2, 3], format_func=lambda x: ["Botadero abierto", "Fosa sin manejo", "Compostaje / Lombricultura"][x-1])
        with c12:
            r_aguas_mieles = st.selectbox("Tratamiento Aguas Mieles", [1, 2, 3], format_func=lambda x: ["Vertimiento directo", "Pozos sépticos", "Sistemas de tratamiento (LPM/Filtros)"][x-1])

        boton_enviar = st.form_submit_button("✅ Finalizar Auditoría y Generar Reporte", type="primary")

    if boton_enviar:
        if not finca:
            st.error("Error: Debe ingresar el nombre de la finca.")
        else:
            # Calcular puntajes
            respuestas = {
                'r_tolva': r_tolva, 'r_aseo': r_aseo, 'r_tec_des': r_tec_des, 
                'r_calib': r_calib, 'r_perdida': r_perdida, 'r_metodo_f': r_metodo_f,
                'r_control_f': r_control_f, 'r_lavado': r_lavado, 'r_tipo_sec': r_tipo_sec,
                'r_humedad': r_humedad, 'r_pulpa': r_pulpa, 'r_aguas_mieles': r_aguas_mieles
            }
            
            imt, d1, d2, d3, d4, d5 = calcular_puntuacion(respuestas)
            
            nuevo_registro = {
                "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Finca": finca, "Municipio": municipio, "IMT": imt,
                "Infraestructura": d1, "Maquinaria": d2, "Fermentacion": d3, "Secado": d4, "Ambiental": d5
            }
            
            st.session_state['base_datos'] = pd.concat([st.session_state['base_datos'], pd.DataFrame([nuevo_registro])], ignore_index=True)
            st.success(f"Auditoría guardada con éxito. Índice de Madurez: {imt}%")
            
            # Gráfico de Radar para el reporte inmediato
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=[d1, d2, d3, d4, d5],
                theta=['Infraestructura', 'Maquinaria', 'Fermentación', 'Secado', 'Ambiental'],
                fill='toself', name=finca
            ))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])))
            st.plotly_chart(fig)

with t2:
    if not st.session_state['base_datos'].empty:
        df = st.session_state['base_datos']
        
        st.subheader("Resumen de Madurez Tecnológica Regional")
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Fincas Auditadas", len(df))
        col_m2.metric("IMT Promedio", f"{round(df['IMT'].mean(),1)}%")
        col_m3.metric("Mejor Dimensión", df[['Infraestructura', 'Maquinaria', 'Fermentacion', 'Secado', 'Ambiental']].mean().idxmax())
        
        st.divider()
        st.dataframe(df, use_container_width=True)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Base de Datos para Tesis (CSV)", csv, "datos_investigacion_mato.csv", "text/csv")
    else:
        st.info("Aún no hay datos. Complete una auditoría para ver el análisis.")
