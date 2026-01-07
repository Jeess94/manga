import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time

st.set_page_config(page_title="Simulador Estable", layout="wide")

# Estilo para eliminar márgenes innecesarios y mejorar la fluidez
st.markdown("""
    <style>
    .stPlotlyChart { margin-top: -20px; }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.header("⚙️ Parámetros de Control")
d_tolva = st.sidebar.slider("Diámetro Tolva (cm)", 30.0, 60.0, 44.0) / 100
h_tolva = 0.80 
d_manga_mayor = st.sidebar.slider("Diámetro Mayor Manga (cm)", 40.0, 70.0, 50.0) / 100
d_manga_menor = st.sidebar.slider("Diámetro Menor Manga (cm)", 20.0, 40.0, 30.0) / 100
descenso_cil = st.sidebar.slider("Descenso Cilindro (cm)", 5.0, 30.0, 10.0) / 100

if st.sidebar.button("▶ Iniciar Proceso"):
    placeholder_grafico = st.empty()
    placeholder_info = st.empty()
    
    nivel_harina = 0.0
    h_plomada = 0.05 
    pos_sensor_final = h_tolva - descenso_cil
    plomada_y = pos_sensor_final
    
    # Pre-generamos las coordenadas de la manga y tolva para no recalcularlas
    x_manga = [-d_manga_mayor/2, d_manga_mayor/2, d_manga_menor/2, -d_manga_menor/2, -d_manga_mayor/2]
    y_manga = [h_tolva+0.2, h_tolva+0.2, h_tolva, h_tolva, h_tolva+0.2]
    
    for t in range(150):
        tocado = nivel_harina >= plomada_y
        
        if not tocado:
            nivel_harina += 0.01
            estado = "📥 LLENANDO TOLVA..."
            color_msg = "#1E90FF"
        else:
            plomada_y = nivel_harina
            nivel_harina += 0.002 
            estado = "🛑 SEÑAL DE NIVEL: CORTE DE ENVÍO"
            color_msg = "#FF4B4B"
        
        fig = go.Figure()

        # 1. Harina (Fondo primero)
        fig.add_shape(type="rect", x0=-d_tolva/2, y0=0, x1=d_tolva/2, y1=nivel_harina,
                      line=dict(width=0), fillcolor="wheat", opacity=0.9)

        # 2. Tolva (Contorno)
        fig.add_shape(type="rect", x0=-d_tolva/2, y0=0, x1=d_tolva/2, y1=h_tolva,
                      line=dict(color="black", width=2))

        # 3. Manga
        fig.add_trace(go.Scatter(x=x_manga, y=y_manga, fill="toself", 
                                 fillcolor='orange', line=dict(color="darkorange"), 
                                 hoverinfo='skip'))

        # 4. Sensor y Plomada
        # Hilo
        fig.add_trace(go.Scatter(x=[0, 0], y=[h_tolva + 0.1, plomada_y + h_plomada],
                                 mode='lines', line=dict(color='blue', width=4), hoverinfo='skip'))
        # Plomada
        fig.add_shape(type="rect", x0=-0.02, y0=plomada_y, x1=0.02, y1=plomada_y + h_plomada,
                      fillcolor="red", line=dict(color="darkred"))

        # 5. Efecto de partículas solo si está llenando
        if not tocado:
            px = np.random.uniform(-d_manga_menor/3, d_manga_menor/3, 8)
            py = np.random.uniform(nivel_harina, h_tolva, 8)
            fig.add_trace(go.Scatter(x=px, y=py, mode='markers', 
                                     marker=dict(color='gray', size=3), hoverinfo='skip'))

        # CONFIGURACIÓN CLAVE PARA EVITAR TITILEO
        fig.update_layout(
            xaxis=dict(range=[-0.6, 0.6], fixedrange=True, visible=False),
            yaxis=dict(range=[0, 1.1], fixedrange=True, visible=False),
            height=600,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            uirevision='constant', # <--- Mantiene el estado del gráfico
            margin=dict(l=50, r=50, t=20, b=20)
        )
        
        # Usamos theme=None para que Streamlit no intente aplicar estilos extra cada vez
        placeholder_grafico.plotly_chart(fig, use_container_width=True, theme=None, config={'displayModeBar': False})
        placeholder_info.markdown(f"<h2 style='color:{color_msg}; text-align:center;'>{estado}</h2>", unsafe_allow_html=True)
        
        if nivel_harina >= h_tolva: break
        time.sleep(0.02) # Un poco más rápido para mayor fluidez

else:
    st.info("Configura las medidas y presiona 'Iniciar Proceso'.")
