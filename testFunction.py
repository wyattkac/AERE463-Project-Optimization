# Script to test the RadarSimPy_Function function from RadarSimPyFunction.py

from RadarSimPyFunction import RadarSimPy_Function

target = {
    "model": 'C:/Users/Nicholas/Documents/ISU Spring 2024/AERE 463/AERE463-Project-Optimization/Example_Mesh1.stl',
    "location": (0, 0, 0),
}

RadarSimPy_Function(target)