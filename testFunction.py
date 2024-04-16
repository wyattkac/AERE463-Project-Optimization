# Script to test the RadarSimPy_Function function from RadarSimPyFunction.py

from RadarSimPyFunction import RadarSimPy_Function

target = {
    "model": 'C:/Users/Nicholas/Documents/ISU Spring 2024/AERE 463/AERE463-Project-Optimization/test_vehicle_mesh.stl',
    "location": (0, 0, 0),
}

[average_rcs, max_rcs] = RadarSimPy_Function(target)