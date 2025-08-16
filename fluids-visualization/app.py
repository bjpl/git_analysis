import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("2D Potential Flow Visualizer")
st.write("""
Adjust the parameters to explore the flow around a circular obstacle.
You can download the resulting velocity field for your own analysis.
""")

# Sidebar controls
st.sidebar.header("Obstacle Parameters")
obs_radius = st.sidebar.slider("Obstacle Radius", 0.05, 1.0, 0.5, 0.01)
obs_x = st.sidebar.slider("Obstacle X Position", -1.5, 1.5, 0.0, 0.01)
obs_y = st.sidebar.slider("Obstacle Y Position", -1.5, 1.5, 0.0, 0.01)

st.sidebar.header("Flow Parameters")
U_inf = st.sidebar.slider("Free Stream Velocity (U_inf)", 0.1, 2.0, 1.0, 0.01)
angle = st.sidebar.slider("Flow Angle (degrees)", 0, 360, 0, 1)

# Grid
nx, ny = 80, 80
x = np.linspace(-2, 2, nx)
y = np.linspace(-2, 2, ny)
X, Y = np.meshgrid(x, y)

# Adjust flow direction
theta_flow = np.radians(angle)
Ux = U_inf * np.cos(theta_flow)
Uy = U_inf * np.sin(theta_flow)

# Compute flow
R = np.sqrt((X - obs_x)**2 + (Y - obs_y)**2)
theta = np.arctan2(Y - obs_y, X - obs_x)

with np.errstate(divide='ignore', invalid='ignore'):
    u_r = (Ux * np.cos(theta) + Uy * np.sin(theta)) * (1 - (obs_radius**2) / (R**2))
    u_theta = (-Ux * np.sin(theta) + Uy * np.cos(theta)) * (1 + (obs_radius**2) / (R**2))
    U = u_r * np.cos(theta) - u_theta * np.sin(theta)
    V = u_r * np.sin(theta) + u_theta * np.cos(theta)
    U[R < obs_radius] = np.nan
    V[R < obs_radius] = np.nan

speed = np.hypot(U, V)

# Visualization
fig, ax = plt.subplots(figsize=(6, 6))
strm = ax.streamplot(X, Y, U, V, color=speed, linewidth=1.2, cmap='viridis', density=2)
circle = plt.Circle((obs_x, obs_y), obs_radius, color='gray', zorder=10)
ax.add_patch(circle)
ax.set_xlim(-2, 2)
ax.set_ylim(-2, 2)
ax.set_aspect('equal')
ax.set_title("Potential Flow Around a Circular Obstacle")
ax.set_xlabel("x")
ax.set_ylabel("y")
cbar = fig.colorbar(strm.lines, ax=ax, label="Speed")

st.pyplot(fig)

# Downloadable data
st.subheader("Download Velocity Field Data")
import pandas as pd

df = pd.DataFrame({
    "x": X.flatten(),
    "y": Y.flatten(),
    "U": U.flatten(),
    "V": V.flatten(),
    "speed": speed.flatten(),
})
csv = df.to_csv(index=False)
st.download_button(
    label="Download CSV",
    data=csv,
    file_name="velocity_field.csv",
    mime="text/csv",
)

st.markdown("""
---
**How does this help you?**

- Visualize and analyze flow around obstacles for teaching, research, or engineering
- Export velocity data for post-processing (e.g., in Excel, Python, MATLAB)
- Explore the effects of changing flow angle, speed, or obstacle geometry
- Use images in reports/presentations
""")
