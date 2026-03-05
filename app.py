import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Auditoría MATO - Café", page_icon="☕", layout="wide")

# --- ESTILOS PERSONALIZADOS (Corregido: unsafe_allow_html) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAR MEMORIA TEMPORAL ---
if 'db' not in st.session_state:
    st.session_state['db'] = pd.DataFrame(columns=[
        "Fecha", "Finca", "Municipio", "IMT_Total", "Infraestructura", "Maquinaria", "Procesos"
    ])

# --- LÓGICA DE CÁLCULO ---
def calcular_metricas(datos):
    # Escala 0-100 por dimensión
    p_infra = (datos['tolva'] / 3) * 100
    p_maq = ((datos['desp_tec'] + datos['desp_cal']) / 6) * 100
    p_proc = ((datos['ferm'] + datos['secado']) / 6) * 100
    
    # Índice de Madurez Tecnológica (IMT) con pesos ponderados
    imt = (p_infra * 0.20) + (p_maq * 0.40) + (p_proc * 0.40)
    return round(imt, 1), round(p_infra, 1), round(p_maq, 1), round(p_proc, 1)

# --- TÍTULO Y EXPLICACIÓN ---
st.title("🔬 Sistema de Auditoría MATO")
st.caption("Herramienta de recolección de datos - Provincia de Vélez, Santander")

tab1, tab2 = st.tabs(["📝 Nueva Auditoría", "📊 Tablero de Resultados"])

with tab1:
    with st.form("form_investigacion", clear_on_submit=True):
        st.subheader("1. Información de Campo")
        c1, c2 = st.columns(2)
        with c1:
            finca = st.text_input("Nombre de la Finca / Productor")
        with c2:
            municipio = st.selectbox("Municipio", ["Vélez", "Guavatá", "Jesús María", "Chipatá", "La Belleza"])

        st.divider()
        st.subheader("2. Evaluación de Dimensiones")
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown("**Infraestructura**")
            tolva = st.radio("Material Tolva", [1, 2, 3], 
                             format_func=lambda x: ["Madera", "Cemento", "Acero/Epóxico"][x-1])
        with col_b:
            st.markdown("**Maquinaria**")
            d_tec = st.selectbox("Tecnología Despulpado", [1, 2, 3], 
                                 format_func=lambda x: ["Tradicional", "Cilindro", "Ecológica"][x-1])
            d_cal = st.select_slider("Estado Calibración", options=[1, 2, 3], value=2)
        with col_c:
            st.markdown("**Procesos**")
            ferm = st.radio("Control Fermentación", [1, 2, 3], 
                            format_func=lambda x: ["Empírico", "Lavado", "pH/Fermaestro"][x-1])
            secado = st.selectbox("Tecnología Secado", [1, 2, 3], 
                                  format_func=lambda x: ["Patio/Suelo", "Marquesina", "Silo/Zarandas"][x-1])

        enviar = st.form_submit_button("Registrar Auditoría", type="primary")

    if enviar:
        if not finca:
            st.warning("⚠️ El nombre de la finca es obligatorio.")
        else:
            # Procesar datos
            imt, p_inf, p_maq, p_proc = calcular_metricas({
                'tolva': tolva, 'desp_tec': d_tec, 'desp_cal': d_cal, 
                'ferm': ferm, 'secado': secado
            })
            
            # Guardar
            nuevo = {
                "Fecha": datetime.now().strftime("%Y-%m-%d"),
                "Finca": finca, "Municipio": municipio, "IMT_Total": imt,
                "Infraestructura": p_inf, "Maquinaria": p_maq, "Procesos": p_proc
            }
            st.session_state['db'] = pd.concat([st.session_state['db'], pd.DataFrame([nuevo])], ignore_index=True)
            
            st.success(f"✅ Auditoría de '{finca}' registrada con éxito.")

            # --- GRÁFICO DE RADAR ---
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=[p_inf, p_maq, p_proc],
                theta=['Infraestructura', 'Maquinaria', 'Procesos'],
                fill='toself',
                name=finca,
                line_color='#795548'
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    if not st.session_state['db'].empty:
        df = st.session_state['db']
        
        # Métricas principales
        m1, m2 = st.columns(2)
        m1.metric("Fincas Auditadas", len(df))
        m2.metric("Promedio Regional IMT", f"{round(df['IMT_Total'].mean(), 1)}%")
        
        st.divider()
        st.dataframe(df, use_container_width=True)
        
        # Exportación
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Base de Datos (CSV)",
            data=csv,
            file_name=f"Datos_MATO_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
    else:
        st.info("No hay datos registrados todavía.")
