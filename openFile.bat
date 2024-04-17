cd "C:\Users\wyatt\OneDrive\Documents\463\OpenVSP-3.37.1-win64-Python3.11\OpenVSP-3.37.1-win64"
start cmd /k vsp.exe C:\Users\wyatt\OneDrive\Documents\GitHub\AERE463-Project-Optimization\test_vehicle.vsp3 ^& exit
timeout /t 15
taskkill /im vsp.exe /f