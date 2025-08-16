import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Flujo Laminar en Tubería", layout="centered")

st.title("Perfil de velocidad en una tubería cilíndrica")

R = st.slider('Radio de la tubería (cm)', min_value=0.5, max_value=10.0, value=3.0, step=0.1)
deltaP = st.slider('Diferencia de presión (Pa)', min_value=10, max_value=500, value=100, step=10)
L = st.slider('Longitud de la tubería (m)', min_value=0.1, max_value=5.0, value=1.0, step=0.1)
mu = st.slider('Viscosidad dinámica (mPa·s)', min_value=0.1, max_value=10.0, value=1.0, step=0.1)

R_m = R / 100
mu_Pa_s = mu / 1000

# Malla transversal circular
N = 200
x = np.linspace(-R_m, R_m, N)
y = np.linspace(-R_m, R_m, N)
X, Y = np.meshgrid(x, y)
r = np.sqrt(X**2 + Y**2)

Vmax = (deltaP * R_m**2) / (4 * mu_Pa_s * L)
V = np.zeros_like(r)
V[r <= R_m] = Vmax * (1 - (r[r <= R_m]**2) / (R_m**2))
V[r > R_m] = np.nan

fig, ax = plt.subplots(figsize=(6, 6))
c = ax.imshow(V, extent=[-R, R, -R, R], origin='lower', cmap='plasma', alpha=0.9)
fig.colorbar(c, ax=ax, label='Velocidad axial (m/s)')
circle = plt.Circle((0, 0), R, color='black', fill=False, linewidth=2)
ax.add_patch(circle)
ax.set_xlabel('x (cm)')
ax.set_ylabel('y (cm)')
ax.set_title('Perfil de velocidad (más claro = más rápido)')
ax.set_aspect('equal')
st.pyplot(fig)
st.markdown(f"**Velocidad máxima (centro):** {Vmax:.3f} m/s")
