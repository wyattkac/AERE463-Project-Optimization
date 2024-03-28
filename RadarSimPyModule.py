# %%
import radarsimpy
print('`RadarSimPy` used in this example is version: ' +
      str(radarsimpy.__version__))

# %%
import pymeshlab
import numpy as np

target = {

        "model": 'C:/Users/Nicholas/Documents/ISU Spring 2024/AERE 463/AERE463-Project-Optimization/Example_Mesh1.stl',
        "location": (0, 0, 0),
  }

# %%
# import plotly.graph_objs as go
# from IPython.display import Image

# ms = pymeshlab.MeshSet()
# ms.load_new_mesh(target['model'])
# t_mesh = ms.current_mesh()
# v_matrix = np.array(t_mesh.vertex_matrix())
# f_matrix = np.array(t_mesh.face_matrix())

# fig = go.Figure()
# fig.add_trace(go.Mesh3d(x=v_matrix[:, 0],
#                         y=v_matrix[:, 1],
#                         z=v_matrix[:, 2],
#                         i=f_matrix[:, 0],
#                         j=f_matrix[:, 1],
#                         k=f_matrix[:, 2],
#                         intensity=v_matrix[:, 2],
#                         colorscale='Viridis'
#                         ))
# fig['layout']['scene']['aspectmode'] = "data"
# fig['layout']['height'] = 800

# # uncomment this to display interactive plot
# fig.show()

# # Simulate RCS vs Observation Angle
# %%
import time

from radarsimpy.rt import rcs_sbr
import numpy as np

phi = np.arange(0, 180, 1)
theta = 90
freq = 3.1e9
pol = [0, 0, 1]
density = .1

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

rcs = np.concatenate((rcs, rcs))
phi = np.concatenate((phi, -phi))

average_rcs = np.mean(rcs)
print(average_rcs)
np.savetxt('average_rcs.txt', [average_rcs], fmt='%.18f')

max_rcs = np.max(rcs)
print(max_rcs)
np.savetxt('max_rcs.txt', [max_rcs], fmt='%.18f')



# %%
import plotly.graph_objs as go
import plotly.express as px
fig = go.Figure()

fig = px.line_polar(r=rcs,                   
                    theta=phi,
                    line_close=True,
                    range_r=[-40, 40],
                    title='RCS vs Observation Angle',
                    labels={'r': 'RCS (dBsm)', 'theta': 'Observation angle (Degree)'},
                    line_shape='spline',
                        )
                        

fig.update_layout(
    title='RCS vs Observation Angle',
    yaxis=dict(title='RCS (dBsm)'),
    xaxis=dict(title='Observation angle (Degree)', dtick=20),
)

# fig.write_image("figure.png", width=800, height=800, scale=2)
fig.show()
