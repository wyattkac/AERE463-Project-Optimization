# %
# @author: Nicholas McCormick
# @date: 2024-03-28
# @note: This script is used to simulate the radar cross section of an object and derived from an example on the RadarSimPy GitHub page.
# %

import radarsimpy
print('`RadarSimPy` used in this example is version: ' +
      str(radarsimpy.__version__))

# %%
import pymeshlab
import numpy as np

target = {

        "model": 'Example_Mesh1.stl',
        "location": (0, 0, 0),
  }

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

rcs = np.zeros_like(phi, dtype=float)

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
with open('average_rcs.txt', 'a') as file:
    file.write(f"{average_rcs:.18f}\n")

max_rcs = np.max(rcs)
print(max_rcs)
with open('max_rcs.txt', 'a') as file:
    file.write(f"{max_rcs:.18f}\n")



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

fig.show()
