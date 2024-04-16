# Script to test the RadarSimPy_Function function from RadarSimPyFunction.py

from rcsFunc import rcs

target = {
    "model": 'C:/Users/Nicholas/Documents/ISU Spring 2024/AERE 463/AERE463-Project-Optimization/test_vehicle_mesh.stl',
    "location": (0, 0, 0),
}

[average_rcs, max_rcs] = rcs(target)