# Script to test the RadarSimPy_Function function from RadarSimPyFunction.py

from rcsFunc import rcs

target = {
    "model": 'test_vehicle_mesh.stl',
    "location": (0, 0, 0),
}

[average_rcs, max_rcs] = rcs(target)