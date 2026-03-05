import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# -------------------------------
# CONFIGURACIÓN GENERAL
# -------------------------------

st.set_page_config(
    page_title="Auditoría Técnica MATO",
    page_icon="☕",
    layout="wide"
)

st.title("☕ Auditoría Técnica de Beneficiaderos de Café")
st.markdown("### Evaluación del Nivel de Madurez Tecnológica (IMT)")

# -------------------------------
# BASE DE DATOS EN MEMORIA
# -------------------------------

if "base_datos" not in st.session_state:
    st.session_state["base_datos"] = pd.DataFrame()

# -------------------------------
# FUNCIÓN DE CÁLCULO DEL IMT
# -------------------------------

def calcular_puntuacion(respuestas):

    d1 = (respuestas['r_tolva'] + respuestas['r_aseo']) / 6 * 100
    d2 = (respuestas['r_tec_des'] + respuestas['r_calib'] + respuestas['r_perdida']) / 9 * 100
    d3 = (respuestas['r_metodo_f'] + respuestas['r_control_f'] + respuestas['r_lavado']) / 9 * 100
    d4 = (respuestas['r_tipo_sec'] + respuestas['r_humedad']) / 6 * 100
    d5 = (respuestas['r_pulpa'] + respuestas['r_aguas_mieles']) / 6 * 100

    imt = (d1*0.15) + (d2*0.25) + (d3*0.25) + (d4*0.20) + (d5*0.15)

    return round(imt,2), round(d1,1), round(d2,1), round(d3,1), round(d4,1), round(d5,1)

# -------------------------------
# TABS PRINCIPALES
# -------------------------------

t1, t2 = st.tabs(["📋 Formulario de Auditoría", "📊 Análisis de Resultados"])

# ======================================================
# TAB 1 FORMULARIO
# ======================================================

with t1:

    with st.form("formulario_auditoria"):

        st.subheader("Identificación de la finca")

        c1,c2,c3,c4,c5 = st.columns(5)

        with c1:
            finca = st.text_input("Finca / Productor")

        with c2:
            municipio = st.selectbox(
                "Municipio",
                ["Vélez","Guavatá","Jesús María","Chipatá","La Belleza","Florián"]
            )

        with c3:
            altura = st.number_input("Altitud (msnm)",500,2500,1500)

        with c4:
            latitud = st.number_input("Latitud",value=6.0,format="%.6f")

        with c5:
            longitud = st.number_input("Longitud",value=-73.5,format="%.6f")

        st.divider()

        # -----------------------
        # DIMENSION 1
        # -----------------------

        st.subheader("1 Infraestructura")

        c1,c2 = st.columns(2)

        with c1:
            r_tolva = st.select_slider(
                "Calidad de Tolvas",
                options=[1,2,3],
                help="1 madera | 2 cemento | 3 acero"
            )

        with c2:
            r_aseo = st.select_slider(
                "Protocolos de higiene",
                options=[1,2,3]
            )

        # -----------------------
        # DIMENSION 2
        # -----------------------

        st.subheader("2 Despulpado")

        c3,c4,c5 = st.columns(3)

        with c3:
            r_tec_des = st.selectbox(
                "Tecnología",
                [1,2,3],
                format_func=lambda x: [
                    "Pechero tradicional",
                    "Cilindro horizontal",
                    "Módulo ecológico"
                ][x-1]
            )

        with c4:
            r_calib = st.selectbox(
                "Calibración",
                [1,2,3],
                format_func=lambda x:[
                    "Descalibrada",
                    "Aceptable",
                    "Óptima"
                ][x-1]
            )

        with c5:
            r_perdida = st.selectbox(
                "Pérdida de grano",
                [1,2,3],
                format_func=lambda x:[
                    "Alta",
                    "Media",
                    "Mínima"
                ][x-1]
            )

        # -----------------------
        # DIMENSION 3
        # -----------------------

        st.subheader("3 Fermentación")

        c6,c7,c8 = st.columns(3)

        with c6:
            r_metodo_f = st.selectbox(
                "Tipo de tanque",
                [1,2,3],
                format_func=lambda x:[
                    "Rectangular",
                    "Circular",
                    "Acero/plástico"
                ][x-1]
            )

        with c7:
            r_control_f = st.selectbox(
                "Control de fermentación",
                [1,2,3],
                format_func=lambda x:[
                    "Visual",
                    "Tiempo",
                    "Sensores"
                ][x-1]
            )

        with c8:
            r_lavado = st.selectbox(
                "Sistema de lavado",
                [1,2,3],
                format_func=lambda x:[
                    "Correteo",
                    "Tanque",
                    "Lavadora"
                ][x-1]
            )

        # -----------------------
        # DIMENSION 4
        # -----------------------

        st.subheader("4 Secado")

        c9,c10 = st.columns(2)

        with c9:
            r_tipo_sec = st.selectbox(
                "Sistema de secado",
                [1,2,3],
                format_func=lambda x:[
                    "Patio",
                    "Marquesina",
                    "Silo"
                ][x-1]
            )

        with c10:
            r_humedad = st.selectbox(
                "Control humedad",
                [1,2,3],
                format_func=lambda x:[
                    "Al tanteo",
                    "Manual",
                    "Digital"
                ][x-1]
            )

        # -----------------------
        # DIMENSION 5
        # -----------------------

        st.subheader("5 Gestión ambiental")

        c11,c12 = st.columns(2)

        with c11:
            r_pulpa = st.selectbox(
                "Manejo pulpa",
                [1,2,3],
                format_func=lambda x:[
                    "Botadero",
                    "Fosa",
                    "Compostaje"
                ][x-1]
            )

        with c12:
            r_aguas_mieles = st.selectbox(
                "Tratamiento aguas mieles",
                [1,2,3],
                format_func=lambda x:[
                    "Vertimiento directo",
                    "Pozo",
                    "Sistema tratamiento"
                ][x-1]
            )

        boton = st.form_submit_button("Guardar auditoría")

    # ----------------------------------------------------

    if boton:

        if finca == "":
            st.error("Debe ingresar el nombre de la finca")

        else:

            respuestas = {
                'r_tolva': r_tolva,
                'r_aseo': r_aseo,
                'r_tec_des': r_tec_des,
                'r_calib': r_calib,
                'r_perdida': r_perdida,
                'r_metodo_f': r_metodo_f,
                'r_control_f': r_control_f,
                'r_lavado': r_lavado,
                'r_tipo_sec': r_tipo_sec,
                'r_humedad': r_humedad,
                'r_pulpa': r_pulpa,
                'r_aguas_mieles': r_aguas_mieles
            }

            imt,d1,d2,d3,d4,d5 = calcular_puntuacion(respuestas)

            nuevo = {
                "Fecha":datetime.now(),
                "Finca":finca,
                "Municipio":municipio,
                "Altitud":altura,
                "Latitud":latitud,
                "Longitud":longitud,
                "IMT":imt,
                "Infraestructura":d1,
                "Maquinaria":d2,
                "Fermentacion":d3,
                "Secado":d4,
                "Ambiental":d5
            }

            st.session_state["base_datos"] = pd.concat(
                [st.session_state["base_datos"],pd.DataFrame([nuevo])],
                ignore_index=True
            )

            st.success(f"Auditoría guardada — IMT: {imt}%")

            fig = go.Figure()

            fig.add_trace(go.Scatterpolar(
                r=[d1,d2,d3,d4,d5],
                theta=[
                    "Infraestructura",
                    "Maquinaria",
                    "Fermentación",
                    "Secado",
                    "Ambiental"
                ],
                fill="toself"
            ))

            fig.update_layout(
                polar=dict(radialaxis=dict(range=[0,100]))
            )

            st.plotly_chart(fig)

# ======================================================
# TAB 2 ANALISIS
# ======================================================

with t2:

    if not st.session_state["base_datos"].empty:

        df = st.session_state["base_datos"]

        st.subheader("Indicadores generales")

        c1,c2,c3 = st.columns(3)

        c1.metric("Fincas evaluadas",len(df))

        c2.metric("IMT promedio",round(df["IMT"].mean(),1))

        c3.metric("IMT máximo",df["IMT"].max())

        st.divider()

        # ---------------------
        # MAPA
        # ---------------------

        st.subheader("Mapa de beneficiaderos auditados")

        fig = px.scatter_mapbox(
            df,
            lat="Latitud",
            lon="Longitud",
            hover_name="Finca",
            hover_data=["Municipio","IMT"],
            color="IMT",
            size="IMT",
            zoom=7,
            height=500,
            color_continuous_scale="YlGn"
        )

        fig.update_layout(mapbox_style="open-street-map")

        st.plotly_chart(fig,use_container_width=True)

        st.divider()

        st.subheader("Base de datos")

        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Descargar datos CSV",
            csv,
            "datos_auditoria_mato.csv",
            "text/csv"
        )

    else:

        st.info("Aún no hay auditorías registradas")
