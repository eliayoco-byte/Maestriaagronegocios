import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ------------------------------------------------
# CONFIGURACIÓN
# ------------------------------------------------

st.set_page_config(
    page_title="Auditoría Café",
    page_icon="☕",
    layout="centered"
)

st.title("☕ Auditoría de Beneficiadero")
st.write("Evaluación rápida del sistema de beneficio del café")

# ------------------------------------------------
# BASE DE DATOS
# ------------------------------------------------

if "datos" not in st.session_state:
    st.session_state["datos"] = pd.DataFrame()

# ------------------------------------------------
# FUNCION IMT
# ------------------------------------------------

def calcular_imt(r):

    d1 = (r["r_tolva"] + r["r_aseo"]) / 6 * 100
    d2 = (r["r_tec_des"] + r["r_calib"] + r["r_perdida"]) / 9 * 100
    d3 = (r["r_metodo_f"] + r["r_control_f"] + r["r_lavado"]) / 9 * 100
    d4 = (r["r_tipo_sec"] + r["r_humedad"]) / 6 * 100
    d5 = (r["r_pulpa"] + r["r_aguas_mieles"]) / 6 * 100

    imt = (d1*0.15)+(d2*0.25)+(d3*0.25)+(d4*0.20)+(d5*0.15)

    return round(imt,2), d1,d2,d3,d4,d5

# ------------------------------------------------
# FORMULARIO
# ------------------------------------------------

with st.form("encuesta"):

    st.subheader("Datos de la finca")

    finca = st.text_input("Nombre finca / productor")

    municipio = st.selectbox(
        "Municipio",
        ["Vélez","Guavatá","Jesús María","Chipatá","La Belleza","Florián"]
    )

    altura = st.number_input("Altitud (msnm)",500,2500,1500)

    st.subheader("Ubicación")

    lat = st.number_input("Latitud",value=6.0,format="%.6f")
    lon = st.number_input("Longitud",value=-73.5,format="%.6f")

    st.divider()

    st.subheader("Infraestructura")

    r_tolva = st.radio(
        "Tolvas",
        [1,2,3],
        format_func=lambda x:["Madera","Cemento","Acero"][x-1]
    )

    r_aseo = st.radio(
        "Higiene",
        [1,2,3],
        format_func=lambda x:["Sin limpieza","Básica","Desinfección"][x-1]
    )

    st.subheader("Despulpado")

    r_tec_des = st.radio(
        "Tecnología",
        [1,2,3],
        format_func=lambda x:["Pechero","Cilindro","Ecológico"][x-1]
    )

    r_calib = st.radio(
        "Calibración",
        [1,2,3],
        format_func=lambda x:["Mala","Aceptable","Óptima"][x-1]
    )

    r_perdida = st.radio(
        "Pérdida de grano",
        [1,2,3],
        format_func=lambda x:["Alta","Media","Baja"][x-1]
    )

    st.subheader("Fermentación")

    r_metodo_f = st.radio(
        "Tipo tanque",
        [1,2,3],
        format_func=lambda x:["Rectangular","Circular","Acero"][x-1]
    )

    r_control_f = st.radio(
        "Control fermentación",
        [1,2,3],
        format_func=lambda x:["Visual","Tiempo","Sensores"][x-1]
    )

    r_lavado = st.radio(
        "Sistema lavado",
        [1,2,3],
        format_func=lambda x:["Correteo","Tanque","Lavadora"][x-1]
    )

    st.subheader("Secado")

    r_tipo_sec = st.radio(
        "Tipo secado",
        [1,2,3],
        format_func=lambda x:["Patio","Marquesina","Silo"][x-1]
    )

    r_humedad = st.radio(
        "Control humedad",
        [1,2,3],
        format_func=lambda x:["Tanteo","Manual","Digital"][x-1]
    )

    st.subheader("Gestión ambiental")

    r_pulpa = st.radio(
        "Manejo pulpa",
        [1,2,3],
        format_func=lambda x:["Botadero","Fosa","Compostaje"][x-1]
    )

    r_aguas_mieles = st.radio(
        "Aguas mieles",
        [1,2,3],
        format_func=lambda x:["Vertimiento","Pozo","Tratamiento"][x-1]
    )

    guardar = st.form_submit_button("Guardar auditoría")

# ------------------------------------------------
# GUARDAR
# ------------------------------------------------

if guardar:

    respuestas = {
        "r_tolva":r_tolva,
        "r_aseo":r_aseo,
        "r_tec_des":r_tec_des,
        "r_calib":r_calib,
        "r_perdida":r_perdida,
        "r_metodo_f":r_metodo_f,
        "r_control_f":r_control_f,
        "r_lavado":r_lavado,
        "r_tipo_sec":r_tipo_sec,
        "r_humedad":r_humedad,
        "r_pulpa":r_pulpa,
        "r_aguas_mieles":r_aguas_mieles
    }

    imt,d1,d2,d3,d4,d5 = calcular_imt(respuestas)

    nuevo = {
        "fecha":datetime.now(),
        "finca":finca,
        "municipio":municipio,
        "lat":lat,
        "lon":lon,
        "IMT":imt,
        "infraestructura":d1,
        "maquinaria":d2,
        "fermentacion":d3,
        "secado":d4,
        "ambiental":d5
    }

    st.session_state["datos"] = pd.concat(
        [st.session_state["datos"],pd.DataFrame([nuevo])],
        ignore_index=True
    )

    st.success(f"Auditoría guardada — IMT {imt}%")

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=[d1,d2,d3,d4,d5],
        theta=["Infraestructura","Maquinaria","Fermentación","Secado","Ambiental"],
        fill="toself"
    ))

    fig.update_layout(polar=dict(radialaxis=dict(range=[0,100])))

    st.plotly_chart(fig)

# ------------------------------------------------
# MAPA
# ------------------------------------------------

if not st.session_state["datos"].empty:

    st.subheader("Mapa de fincas evaluadas")

    df = st.session_state["datos"]

    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        hover_name="finca",
        hover_data=["municipio","IMT"],
        color="IMT",
        size="IMT",
        zoom=7,
        height=450,
        color_continuous_scale="YlGn"
    )

    fig.update_layout(mapbox_style="open-street-map")

    st.plotly_chart(fig,use_container_width=True)

    st.subheader("Datos registrados")

    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Descargar base de datos",
        csv,
        "auditoria_cafe.csv",
        "text/csv"
    )
