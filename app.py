import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time

st.set_page_config(page_title="Simulador de Carga", layout="wide")

st.sidebar.header("⚙️ Parámetros de Control")
d_tolva = st.sidebar.slider("Diámetro Tolva (cm)", 30.0, 60.0, 44.0) / 100
h_tolva = 0.80 # Altura fija de la tolva
d_manga_mayor = st.sidebar.slider("Diámetro Mayor Manga (cm)", 40.0, 70.0, 50.0) / 100
d_manga_menor = st.sidebar.slider("Diámetro Menor Manga (cm)", 20.0, 40.0, 30.0) / 100
descenso_cil = st.sidebar.slider("Descenso Cilindro (cm)", 5.0, 20.0, 10.0) / 100

if st.sidebar.button("▶ Iniciar Proceso"):
    # Contenedores vacíos para actualizar en tiempo real
    placeholder_grafico = st.empty()
    placeholder_info = st.empty()
    
    nivel_harina = 0.0
    h_plomada = 0.05 # 5 cm
    pos_sensor_inicial = h_tolva - descenso_cil
    plomada_y = pos_sensor_inicial
    
    for t in range(100):
        # Lógica de llenado y movimiento de plomada
        tocado = nivel_harina >= plomada_y
        
        if not tocado:
            nivel_harina += 0.015
            estado = "📥 LLENANDO TOLVA..."
            color_msg = "blue"
        else:
            # La plomada sube con la harina
            plomada_y = nivel_harina
            nivel_harina += 0.005 # Carga residual más lenta
            estado = "🛑 SEÑAL DE NIVEL: CORTE DE ENVÍO"
            color_msg = "red"
        
        # --- Gráfico 3D ---
        fig = go.Figure()

        # 1. Tolva
        z_t = np.linspace(0, h_tolva, 10)
        theta = np.linspace(0, 2*np.pi, 20)
        theta_grid, z_grid = np.meshgrid(theta, z_t)
        fig.add_trace(go.Surface(x=(d_tolva/2)*np.cos(theta_grid), y=(d_tolva/2)*np.sin(theta_grid), z=z_grid, 
                                 opacity=0.2, showscale=False, colorscale=[[0, 'gray'], [1, 'gray']]))

        # 2. Manga (Cono Invertido)
        z_m = np.linspace(h_tolva, h_tolva + 0.2, 10)
        r_m = np.linspace(d_manga_menor/2, d_manga_mayor/2, 10)
        r_grid, z_grid_m = np.meshgrid(r_m, z_m)
        fig.add_trace(go.Surface(x=r_m[:,None]*np.cos(theta), y=r_m[:,None]*np.sin(theta), z=np.tile(z_m[:,None], (1,20)), 
                                 opacity=0.7, showscale=False, colorscale=[[0, 'orange'], [1, 'orange']]))

        # 3. Harina (Puntos)
        px = np.random.uniform(-d_tolva/3, d_tolva/3, 100)
        py = np.random.uniform(-d_tolva/3, d_tolva/3, 100)
        pz = np.random.uniform(0, nivel_harina, 100)
        fig.add_trace(go.Scatter3d(x=px, y=py, z=pz, mode='markers', marker=dict(size=2, color='wheat')))

        # 4. Cilindro y Plomada (5cm) que sube
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[h_tolva + 0.1, plomada_y + h_plomada], 
                                   mode='lines', line=dict(color='blue', width=8)))
        fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[plomada_y + h_plomada/2], 
                                   mode='markers', marker=dict(size=12, color='red', symbol='diamond')))

        fig.update_layout(scene=dict(zaxis=dict(range=[0, 1.1]), aspectmode='manual', aspectratio=dict(x=1, y=1, z=1.5)), 
                          margin=dict(l=0, r=0, b=0, t=0), height=600)
        
        placeholder_grafico.plotly_chart(fig, use_container_width=True)
        placeholder_info.markdown(f"<h2 style='color:{color_msg}; text-align:center;'>{estado}</h2>", unsafe_allow_html=True)
        
        if nivel_harina > h_tolva: break
        time.sleep(0.1)

else:
    st.info("Configura las medidas a la izquierda y pulsa 'Iniciar Proceso'")