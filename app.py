import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time

st.set_page_config(page_title="Simulador de Tolva 2D", layout="wide")

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
    
    for t in range(120):
        tocado = nivel_harina >= plomada_y
        
        if not tocado:
            nivel_harina += 0.012
            estado = "📥 LLENANDO TOLVA..."
            color_msg = "#1E90FF"
        else:
            plomada_y = nivel_harina
            nivel_harina += 0.003 
            estado = "🛑 SEÑAL DE NIVEL: CORTE DE ENVÍO"
            color_msg = "#FF4B4B"
        
        fig = go.Figure()

        # 1. Dibujar Tolva (Rectángulo de perfil)
        fig.add_shape(type="rect", x0=-d_tolva/2, y0=0, x1=d_tolva/2, y1=h_tolva,
                      line=dict(color="RoyalBlue", width=3), fillcolor="LightSlateGray", opacity=0.1)

        # 2. Dibujar Manga (Trapecio invertido)
        fig.add_trace(go.Scatter(
            x=[-d_manga_mayor/2, d_manga_mayor/2, d_manga_menor/2, -d_manga_menor/2, -d_manga_mayor/2],
            y=[h_tolva+0.2, h_tolva+0.2, h_tolva, h_tolva, h_tolva+0.2],
            fill="toself", fillcolor='orange', line=dict(color="darkorange"), name="Manga"
        ))

        # 3. Dibujar Harina (Rectángulo que sube)
        fig.add_shape(type="rect", x0=-d_tolva/2 * 0.98, y0=0, x1=d_tolva/2 * 0.98, y1=nivel_harina,
                      line=dict(width=0), fillcolor="wheat", opacity=0.8)
        
        # 4. Partículas (Efecto visual de caída)
        if not tocado:
            px = np.random.uniform(-d_manga_menor/3, d_manga_menor/3, 15)
            py = np.random.uniform(nivel_harina, h_tolva, 15)
            fig.add_trace(go.Scatter(x=px, y=py, mode='markers', marker=dict(color='wheat', size=4), showlegend=False))

        # 5. Cilindro Interno y Plomada (5cm)
        # Hilo/Cilindro
        fig.add_trace(go.Scatter(x=[0, 0], y=[h_tolva + 0.1, plomada_y + h_plomada],
                                 mode='lines', line=dict(color='blue', width=4), name="Sensor"))
        # Plomada (Rectángulo rojo de 5cm)
        fig.add_shape(type="rect", x0=-0.02, y0=plomada_y, x1=0.02, y1=plomada_y + h_plomada,
                      fillcolor="red", line=dict(color="darkred"))

        # Configuración de los ejes
        fig.update_layout(
            xaxis=dict(range=[-0.5, 0.5], fixedrange=True, title="Ancho (m)"),
            yaxis=dict(range=[0, 1.1], fixedrange=True, title="Altura (m)"),
            height=600,
            showlegend=False,
            plot_bgcolor='white'
        )
        
        placeholder_grafico.plotly_chart(fig, use_container_width=True)
        placeholder_info.markdown(f"<h2 style='color:{color_msg}; text-align:center;'>{estado}</h2>", unsafe_allow_html=True)
        
        if nivel_harina >= h_tolva: break
        time.sleep(0.05)

else:
    st.info("Configura las medidas y presiona 'Iniciar Proceso' para ver la animación en 2D.")
