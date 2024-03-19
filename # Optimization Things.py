# Optimization Things
import radarsimpy
import openvsp as vsp
import pymeshlab
import numpy as np
import plotly.graph_objs as go
from IPython.display import Image
import time
from radarsimpy.rt import rcs_sbr
target = {
        "model": 'C:\\Users\\Nicholas\\Documents\\ISU Spring 2024\\AERE 463\\AERE463-Project-Optimization\\plane.stl',
        "location": (0, 0, 0),
    }

phi = np.arange(0, 180, 1)
theta = 90
freq = 76e9
pol = [0, 0, 1]
density = 0.1

# rcs = np.zeros_like(phi)
# print(len(phi))
# tic = time.time()
# for phi_idx, phi_ang in enumerate(phi):
#     rcs[phi_idx] = 10 * np.log10(
#         rcs_sbr([target],
#                 freq,
#                 phi_ang,
#                 theta,
#                 pol=pol,
#                 density=density))
# toc = time.time()

# print('Exec time :'+str(toc-tic) + 's')

# fig = go.Figure()

# fig.add_trace(go.Scatter(x=phi, y=rcs))

# fig.update_layout(
#     title='RCS vs Observation Angle',
#     yaxis=dict(title='RCS (dBsm)'),
#     xaxis=dict(title='Observation angle (Degree)', dtick=20),
# )