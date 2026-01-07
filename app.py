import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Simulador de Carga de Harina", layout="wide")
st.title("🏗️ Simulador de Tolva y Manga Paramétrico")

# --- PANEL LATERAL (CONTROLES) ---
st.sidebar.header("Configuración de Dimensiones")

# Dimensiones Tolva
d_tolva = st.sidebar.slider("Diámetro Tolva (cm)", 30, 100, 44) / 100
h_tolva = st.sidebar.slider("Altura Tolva (cm)", 40, 150, 80) / 100

# Dimensiones Manga/Cono
d_manga_mayor = st.sidebar.slider("Diámetro Mayor Manga (cm)", 40, 80, 50) / 100
d_manga_menor = st.sidebar.slider("Diámetro Menor Manga (cm)", 20, 50, 30) / 100
h_manga = 0.20 # Altura fija según pedido inicial

# Sensor
descenso_cilindro = st.sidebar.slider("Descenso Cilindro Interno (cm)", 5, 30, 10) / 100
h_plomada = 0.05 # 5 cm según pedido

if st.button("▶️ Iniciar Simulación"):
    progreso_llenado = st.empty()
    grafico_evento = st.empty()
    
    # Simulación de pasos
    pasos = 50
    altura_harina = 0
    plomada_y = h_tolva - descenso_cilindro # Posición objetivo de la plomada
    
    for i in range(pasos + 20):
        # Lógica de llenado
        if altura_harina < plomada_y:
            altura_harina += (h_tolva / pasos)
            estado = "Descargando Harina..."
            color_harina = "wheat"
        else:
            # Una vez toca la plomada, la plomada sube con la harina (se levanta)
            plomada_y = altura_harina
            # Excedente (termina de bajar lo que queda en la manga)
            if i < pasos + 15:
                altura_harina += 0.005
                estado = "¡NIVEL ALCANZADO! (Descargando excedente)"
            else:
                estado = "Proceso Terminado"
        
        # --- CREACIÓN DEL GRÁFICO 3D CON PLOTLY ---
        fig = go.Figure()

        # 1. Dibujar Tolva (Cilindro)
        z = np.linspace(0, h_tolva, 10)
        theta = np.linspace(0, 2*np.pi, 20)
        theta_grid, z_grid = np.meshgrid(theta, z)
        x_tolva = (d_tolva/2) * np.cos(theta_grid)
        y_tolva = (d_tolva/2) * np.sin(theta_grid)
        fig.add_trace(go.Surface(x=x_tolva, y=y_tolva, z=z_grid, opacity=0.3, showscale=False, colorscale=[[0, 'gray'], [1, 'gray']]))

        # 2. Dibujar Manga (Cono Invertido)
        z_m = np.linspace(h_tolva, h_tolva + h_manga, 10)
        r_m = np.linspace(d_manga_menor/2, d_manga_mayor/2, 10)
        r_grid, z_grid_m = np.meshgrid(r_m, z_m)
        theta_m = np.linspace(0, 2*np.pi, 20)
        x_m = r_m[:, None] * np.cos(theta_m)
        y_m = r_m[:, None] * np.sin(theta_m)
        z_m_surf = np.tile(z_m[:, None], (1, 20))
        fig.add_trace(go.Surface(x=x_m, y=y_m, z=z_m_surf, opacity=0.8, showscale=False, colorscale=[[0, 'orange'], [1, 'orange']]))

        # 3. Harina (Micropartículas aleatorias)
        n_particulas = 150
        px = np.random.uniform(-d_tolva/2.5, d_tolva/2.5, n_particulas)
        py = np.random.uniform(-d_tolva/2.5, d_tolva/2.5, n_particulas)
        pz = np.random.uniform(0, altura_harina, n_particulas)
        fig.add_trace(go.Scatter3d(x=px, y=py, z=pz, mode='markers', marker=dict(size=2, color='wheat')))

        # 4. Cilindro Interno y Plomada (5cm)
        # Cilindro (linea gruesa)
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[h_tolva, plomada_y + h_plomada], 
                                   mode='lines', line=dict(color='blue', width=10)))
        # Plomada (Esfera roja de 5cm de alto)
        fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[plomada_y + h_plomada/2], 
                                   mode='markers', marker=dict(size=15, color='red', symbol='diamond')))

        # Configuración de ejes
        fig.update_layout(
            scene=dict(
                zaxis=dict(range=[0, h_tolva + h_manga + 0.1]),
                xaxis=dict(range=[-0.5, 0.5]),
                yaxis=dict(range=[-0.5, 0.5]),
                aspectmode='manual',
                aspectratio=dict(x=1, y=1, z=1.5)
            ),
            margin=dict(l=0, r=0, b=0, t=0),
            showlegend=False
        )

        grafico_evento.plotly_chart(fig, use_container_width=True)
        progreso_llenado.subheader(f"Estado: {estado} | Nivel: {altura_harina*100:.1f} cm")
        
        if "Terminado" in estado:
            st.balloons()
            break
        
        time.sleep(0.05)

else:
    st.info("Ajusta las dimensiones en el panel de la izquierda y presiona 'Iniciar Simulación'")