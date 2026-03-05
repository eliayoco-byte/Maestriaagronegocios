import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Auditoría MATO - Café", page_icon="☕", layout="wide")

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_index=True)

# --- INICIALIZAR SESIÓN ---
if 'db' not in st.session_state:
    st.session_state['db'] = pd.DataFrame(columns=[
        "Fecha", "Finca", "Municipio", "IMT_Total", "Infraestructura", "Maquinaria", "Procesos"
    ])

# --- LÓGICA DE CÁLCULO CIENTÍFICO ---
def calcular_metricas(datos):
    # Ponderaciones sugeridas para una tesis (puedes ajustarlas)
    p_infra = (datos['tolva'] / 3) * 100
    p_maq = ((datos['desp_tec'] + datos['desp_cal']) / 6) * 100
    p_proc = ((datos['ferm'] + datos['secado']) / 6) * 100
    
    # Índice de Madurez Tecnológica (IMT) - Promedio ponderado
    imt = (p_infra * 0.20) + (p_maq * 0.40) + (p_proc * 0.40)
    return round(imt, 1), round(p_infra, 1), round(p_maq, 1), round(p_proc, 1)

# --- INTERFAZ PRINCIPAL ---
st.title("🔬 Sistema de Auditoría MATO")
st.caption("Herramienta de recolección de datos para investigación de maestría - Provincia de Vélez")

tab1, tab2 = st.tabs(["📝 Nueva Auditoría", "📊 Tablero de Resultados"])

with tab1:
    with st.form("form_investigacion"):
        st.subheader("1. Información de Campo")
        c1, c2, c3 = st.columns(3)
        with c1:
            finca = st.text_input("Nombre de la Finca / Productor")
        with c2:
            municipio = st.selectbox("Municipio", ["Vélez", "Guavatá", "Jesús María", "Chipatá", "La Belleza"])
        with c3:
            volumen = st.number_input("Producción (Kg Cereza/Día)", min_value=0)

        st.divider()
        st.subheader("2. Dimensiones Técnicas")
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown("**Infraestructura**")
            tolva = st.radio("Estado Tolvas", [1, 2, 3], 
                             help="1: Madera, 2: Cemento, 3: Acero/Epóxico")
        with col_b:
            st.markdown("**Maquinaria**")
            d_tec = st.selectbox("Tecnología Despulpado", [1, 2, 3], format_func=lambda x: ["Tradicional", "Cilindro", "Ecológica"][x-1])
            d_cal = st.select_slider("Calibración", options=[1, 2, 3])
        with col_c:
            st.markdown("**Procesos**")
            ferm = st.radio("Fermentación", [1, 2, 3], help="1: Empírica, 2: Lavado simple, 3: Controlada (pH)")
            secado = st.selectbox("Secado", [1, 2, 3], format_func=lambda x: ["Suelo", "Marquesina", "Mecánico"][x-1])

        enviar = st.form_submit_button("Registrar Auditoría", type="primary")

    if enviar:
        if not finca:
            st.warning("⚠️ Por favor ingresa el nombre de la finca.")
        else:
            # Calcular resultados
            imt, p_inf, p_maq, p_proc = calcular_metricas({
                'tolva': tolva, 'desp_tec': d_tec, 'desp_cal': d_cal, 
                'ferm': ferm, 'secado': secado
            })
            
            # Guardar en memoria
            nuevo = {
                "Fecha": datetime.now().strftime("%Y-%m-%d"),
                "Finca": finca, "Municipio": municipio, "IMT_Total": imt,
                "Infraestructura": p_inf, "Maquinaria": p_maq, "Procesos": p_proc
            }
            st.session_state['db'] = pd.concat([st.session_state['db'], pd.DataFrame([nuevo])], ignore_index=True)
            
            st.success(f"✅ Auditoría de '{finca}' registrada con éxito.")

            # --- VISUALIZACIÓN RÁPIDA (RADAR) ---
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=[p_inf, p_maq, p_proc],
                theta=['Infraestructura', 'Maquinaria', 'Procesos'],
                fill='toself',
                name=finca,
                line_color='#4E342E'
            ))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    if not st.session_state['db'].empty:
        df = st.session_state['db']
        
        # Métricas Globales
        m1, m2 = st.columns(2)
        m1.metric("Total Fincas Auditadas", len(df))
        m2.metric("Promedio Madurez (IMT)", f"{round(df['IMT_Total'].mean(), 1)}%")
        
        st.divider()
        st.subheader("Datos recolectados")
        st.dataframe(df, use_container_width=True)
        
        # Botón de Descarga
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Base de Datos para Tesis (CSV)",
            data=csv,
            file_name=f"Auditoria_MATO_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
    else:
        st.info("Aún no hay datos registrados. Por favor completa el formulario.")
