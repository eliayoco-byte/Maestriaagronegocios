import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Auditoría MATO - Maestría", page_icon="☕", layout="wide")

# --- FUNCIONES DE PERSISTENCIA ---
FILE_NAME = "database_mato_velez.csv"

def guardar_datos(nuevo_registro):
    df = pd.DataFrame([nuevo_registro])
    if not os.path.isfile(FILE_NAME):
        df.to_csv(FILE_NAME, index=False, sep=";")
    else:
        df.to_csv(FILE_NAME, mode='a', index=False, header=False, sep=";")

# --- LÓGICA DE CÁLCULO (PESOS TEÓRICOS) ---
# Se asignan pesos según importancia técnica para el objetivo de la maestría
def calcular_puntajes(datos):
    # Escala de 0 a 100
    p_infra = (datos['Tolva_Material'] / 3) * 100
    p_maquinaria = ((datos['Despulpado_Tec'] + datos['Despulpado_Calibracion']) / 6) * 100
    p_proceso = ((datos['Fermentacion_Control'] / 2) * 0.5 + (datos['Secado_Tec'] / 4) * 0.5) * 100
    
    score_total = (p_infra * 0.2) + (p_maquinaria * 0.4) + (p_proceso * 0.4)
    return round(score_total, 2), round(p_infra, 2), round(p_maquinaria, 2), round(p_proceso, 2)

# --- INTERFAZ ---
st.title("🔬 MATO: Modelo de Auditoría Técnico-Operativa")
st.markdown("""
Esta herramienta evalúa el nivel de madurez tecnológica de los beneficiaderos de café. 
*Provincia de Vélez, Santander.*
""")

tabs = st.tabs(["📝 Captura de Datos", "📊 Análisis en Tiempo Real", "📂 Base de Datos Histórica"])

with tabs[0]:
    with st.form("main_form"):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📍 Identificación")
            finca = st.text_input("Nombre de la Finca / Productor")
            municipio = st.selectbox("Municipio", ["Vélez", "Guavatá", "Jesús María", "La Belleza", "Chipatá"])
            coordenadas = st.text_input("Coordenadas GPS (Lat, Long)", placeholder="6.0123, -73.6789")
        
        with col2:
            st.subheader("📈 Capacidad")
            volumen = st.number_input("Volumen Pico (Kg Cereza/día)", min_value=0)
            variedad = st.multiselect("Variedades", ["Castillo", "Cenicafé 1", "Colombia", "Típica", "Borbón"])

        st.divider()
        
        col3, col4, col5 = st.columns(3)
        with col3:
            st.markdown("**Infraestructura**")
            tolva = st.radio("Material Tolva", [1, 2, 3], format_func=lambda x: ["Madera", "Cemento", "Acero/Epóxico"][x-1])
        
        with col4:
            st.markdown("**Maquinaria**")
            d_tec = st.selectbox("Tecnología Despulpado", [1, 2, 3], format_func=lambda x: ["Tradicional", "Cilindro", "Ecológico BECO"][x-1])
            d_cal = st.select_slider("Estado de Calibración", options=[1, 2, 3], value=2)

        with col5:
            st.markdown("**Proceso de Calidad**")
            ferm = st.radio("Control Fermentación", [1, 2], format_func=lambda x: ["Empírico", "Instrumentado (pH/Fermaestro)"][x-1])
            sec = st.selectbox("Tecnología Secado", [1, 2, 3, 4], format_func=lambda x: ["Suelo", "Marquesina", "Zarandas", "Silo"][x-1])

        submit = st.form_submit_button("Finalizar Auditoría y Calcular Índice", type="primary")

    if submit:
        if not finca:
            st.error("El nombre de la finca es requerido.")
        else:
            # Cálculos
            dict_datos = {
                "Tolva_Material": tolva, "Despulpado_Tec": d_tec, 
                "Despulpado_Calibracion": d_cal, "Fermentacion_Control": ferm, "Secado_Tec": sec
            }
            total, p_inf, p_maq, p_proc = calcular_puntajes(dict_datos)
            
            registro = {
                "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Finca": finca, "Municipio": municipio, "Coordenadas": coordenadas,
                "Volumen": volumen, "IMT_Total": total, "Infraestructura": p_inf,
                "Maquinaria": p_maq, "Procesos": p_proc, 
                "Raw_Data": str(dict_datos)
            }
            
            guardar_datos(registro)
            st.success(f"✅ Auditoría completada. Índice de Madurez Tecnológica: {total}%")
            
            # --- GRÁFICO DE RADAR PARA EL FEEDBACK INMEDIATO ---
            categories = ['Infraestructura', 'Maquinaria', 'Procesos']
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=[p_inf, p_maq, p_proc],
                theta=categories,
                fill='toself',
                name=finca
            ))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=True)
            st.plotly_chart(fig)

with tabs[1]:
    st.subheader("Análisis Comparativo")
    if os.path.isfile(FILE_NAME):
        df_view = pd.read_csv(FILE_NAME, sep=";")
        st.bar_chart(df_view.set_index("Finca")["IMT_Total"])
        
        avg_imt = df_view["IMT_Total"].mean()
        st.metric("Promedio Regional IMT", f"{round(avg_imt, 2)}%")
    else:
        st.info("No hay datos para analizar aún.")

with tabs[2]:
    st.subheader("Gestión de Datos (Exportar para SPSS/Excel)")
    if os.path.isfile(FILE_NAME):
        df_hist = pd.read_csv(FILE_NAME, sep=";")
        st.dataframe(df_hist)
        
        st.download_button(
            label="Descargar Base de Datos Completa",
            data=df_hist.to_csv(index=False).encode('utf-8'),
            file_name=f"Auditoria_MATO_Master_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("Archivo de base de datos no encontrado.")
