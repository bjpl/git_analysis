import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Flujo Laminar en Tubería", layout="centered")

st.title("Visualización del Flujo Laminar en una Tubería Cilíndrica")

# Parámetros ajustables
R = st.slider('Radio de la tubería (cm)', min_value=0.5, max_value=10.0, value=2.5, step=0.1)
L = st.slider('Longitud de la tubería (m)', min_value=0.1, max_value=5.0, value=1.0, step=0.1)
deltaP = st.slider('Diferencia de presión (Pa)', min_value=10, max_value=500, value=100, step=10)
mu = st.slider('Viscosidad dinámica (mPa·s)', min_value=0.1, max_value=10.0, value=1.0, step=0.1)

# Conversión de unidades
R_m = R / 100   # a metros
mu_Pa_s = mu / 1000  # a Pa·s

# Perfil de velocidad
r = np.linspace(0, R_m, 100)
Vmax = (deltaP * R_m**2) / (4 * mu_Pa_s * L)
v = Vmax * (1 - (r**2) / (R_m**2))

# Caudal volumétrico (Q)
Q = (np.pi * deltaP * R_m**4) / (8 * mu_Pa_s * L)

# Gráfica
fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(r*100, v*100, lw=2)
ax.set_xlabel('Radio (cm)')
ax.set_ylabel('Velocidad (cm/s)')
ax.set_title('Perfil de velocidades del flujo')
ax.grid(True)

st.pyplot(fig)

st.markdown(f"**Caudal volumétrico:** {Q*1e6:.2f} cm³/s")
st.markdown(f"**Velocidad máxima en el centro:** {Vmax*100:.2f} cm/s")
