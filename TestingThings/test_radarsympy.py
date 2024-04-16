import radarsimpy
import openvsp as vsp
import pymeshlab
import numpy as np

print('`RadarSimPy` used in this example is version: ' +
      str(radarsimpy.__version__))

target = {
        "model": 'C:\\Users\\Nicholas\\Documents\\ISU Spring 2024\\AERE 463\\AERE463-Project-Optimization\\lamborgini_aventador.stl',
        "location": (0, 0, 0),
    }

import plotly.graph_objs as go
from IPython.display import Image

ms = pymeshlab.MeshSet()
ms.load_new_mesh(target['model'])
t_mesh = ms.current_mesh()
v_matrix = np.array(t_mesh.vertex_matrix())
f_matrix = np.array(t_mesh.face_matrix())

fig = go.Figure()
fig.add_trace(go.Mesh3d(x=v_matrix[:, 0],
                        y=v_matrix[:, 1],
                        z=v_matrix[:, 2],
                        i=f_matrix[:, 0],
                        j=f_matrix[:, 1],
                        k=f_matrix[:, 2],
                        intensity=v_matrix[:, 2],
                        colorscale='Viridis'
                        ))
fig['layout']['scene']['aspectmode'] = "data"
fig['layout']['height'] = 800

# uncomment this to display interactive plot
fig.show()

# display static image to reduce size on radarsimx.com
# img_bytes = fig.to_image(format="jpg", scale=2)

import time

from radarsimpy.rt import rcs_sbr

phi = np.arange(0, 180, 1)
theta = 90
freq = 76e9
pol = [0, 0, 1]
density = 0.1

rcs = np.zeros_like(phi)
tic = time.time()
for phi_idx, phi_ang in enumerate(phi):
    rcs[phi_idx] = 10 * np.log10(
        rcs_sbr([target],
                freq,
                phi_ang,
                theta,
                pol=pol,
                density=density))
toc = time.time()

print('Exec time :'+str(toc-tic) + 's')

fig = go.Figure()

fig.add_trace(go.Scatter(x=phi, y=rcs))

fig.update_layout(
    title='RCS vs Observation Angle',
    yaxis=dict(title='RCS (dBsm)'),
    xaxis=dict(title='Observation angle (Degree)', dtick=20),
)

# uncomment this to display interactive plot
fig.show()

# display static image to reduce size on radarsimx.com
# img_bytes = fig.to_image(format="jpg", scale=2)
