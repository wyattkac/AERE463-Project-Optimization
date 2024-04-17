"""
@author: wtk
"""
# Import Stuff
import subprocess, os, csv
import openmdao.api as om
import fileinput
import openvsp as vsp
import time

def AeroAnal(ThickChord, Camber, CamberLoc, TotalChord, TotalSpan, Twist, AoA):
    """
    Code to create an aircraft and run the aerodynamic analysis using the OpenVSP API.
    Takes aircraft paramaters as input, and saves STL and VSP3 files for the aircraft
    Runs an aerodynamic analysis, and saves CSV file of coefficents

    :param int ThickChord: Chord Thickness of the Airfoil
    :param Camber: Camber of the Airfoil
    :param CamberLoc: Location of the Camber on the Airfoil
    :param TotalChord: The Chord Length of the Wing
    :param TotalSpan: The Total Span of the Wing
    :param Twist: The Incidence Angle of the Wing
    """
    vsp.ClearVSPModel()
    # Setup Vehicle ------------------------------------------------------------------------------------
    print("\tSetting vehicle parameters.")
    # Setup Pod
    pod_id = vsp.AddGeom("POD", "")
    vsp.SetParmVal(pod_id, "FineRatio", "Design", 20)
    wing_id = vsp.AddGeom("WING", pod_id)
    #   Param for NACA 4 Series Airfoil
    vsp.SetParmVal(wing_id, "ThickChord", "XSecCurve_0", ThickChord) #Range of 0 to 1
    vsp.SetParmVal(wing_id, "Camber", "XSecCurve_0", Camber) #Range of 0 to 0.09
    vsp.SetParmVal(wing_id, "CamberLoc", "XSecCurve_0", CamberLoc) #Range of 0.1 to 0.9
    #   Param for Wing
    vsp.SetParmVal(wing_id, "TotalChord", "WingGeom", TotalChord)
    #TODO
    #vsp.SetParmVal(wing_id, "Root_Chord", "XSec_1", 1.9)
    #TODO
    #vsp.SetParmVal(wing_id, "Tip_Chord", "XSec_1", 1.9)
    vsp.SetParmVal(wing_id, "TotalSpan", "WingGeom", TotalSpan)
    #TODO
    #vsp.SetParmVal(wing_id, "Sweep", "XSec_1", 10 ) #Range of -89 to 89
    vsp.SetParmVal(wing_id, "Twist", "XSec_0", Twist) #Angle of Incidence
    #TODO
    vsp.SetParmVal(wing_id, "X_Rel_Location", "XForm", 2.5) #Range of 0 to 10-Chord
    #   Params for Accuracy
    vsp.SetParmVal(wing_id, "SectTess_U", "XSec_1", 12) #Number of spanwise sections
    #vsp.SetParmVal(wing_id, "Density", "Mass_Props", 1)
    elev_id = vsp.AddGeom("WING", pod_id)
    vsp.SetParmVal(elev_id, "X_Rel_Location", "XForm", 8)
    #TODO
    vsp.SetParmVal(elev_id, "TotalArea", "WingGeom", .4*TotalChord*(TotalSpan*TotalChord)/(8.2-2.5))
    vsp.SetParmVal(elev_id, "SectTess_U", "XSec_1", 12)
    rudd_id = vsp.AddGeom("WING", pod_id)
    vsp.SetParmVal(rudd_id, "Sym_Planar_Flag", "Sym", 0.0 ) #Make it not symmetic (just half an airfoil)
    vsp.SetParmVal(rudd_id, "X_Rel_Rotation", "XForm", 90) #Rotate it vertically 
    vsp.SetParmVal(rudd_id, "X_Rel_Location", "XForm", 8.2)
    #TODO
    vsp.SetParmVal(rudd_id, "TotalArea", "WingGeom", .03*TotalSpan*(TotalSpan*TotalChord)/(8.2-2.5))
    vsp.SetParmVal(rudd_id, "SectTess_U", "XSec_1", 12)
    vsp.Update()
    # Setup and Run Aerodynamic Analysis ---------------------------------------------------------------
    # Setup an Aero Analysis (Compute Geometry)
    compgeom_name = "VSPAEROComputeGeometry"
    print("\tStarting:", compgeom_name)
    # Set defaults
    vsp.SetAnalysisInputDefaults(compgeom_name)
    # Analysis method
    analysis_method = list(vsp.GetIntAnalysisInput(compgeom_name, "AnalysisMethod"))
    analysis_method[0] = vsp.VORTEX_LATTICE
    vsp.SetIntAnalysisInput(compgeom_name, "AnalysisMethod", analysis_method)
    # list inputs, type, and current values
    #vsp.PrintAnalysisInputs(compgeom_name)
    # Execute
    print("\t\tExecuting...", end="")
    compgeom_resid = vsp.ExecAnalysis(compgeom_name)
    print("COMPLETE")
    # Get & Display Results
    #vsp.PrintResults(compgeom_resid)
    # Run the Aerodynamic Analysis (VSPAero Sweep)
    analysis_name = "VSPAEROSweep"
    vsp.SetAnalysisInputDefaults(analysis_name)
    #// Reference geometry set
    geom_set = []
    geom_set.append(0)
    vsp.SetIntAnalysisInput(analysis_name, "GeomSet", geom_set, 0)
    ref_flag = []
    ref_flag.append(1)
    vsp.SetIntAnalysisInput(analysis_name, "RefFlag", ref_flag, 0)
    #TODO
    wid = wing_id#vsp.FindGeomsWithName("WingGeom")
    vsp.SetStringAnalysisInput(analysis_name, "WingID", wid, 0)
    #// Freestream Parameters
    alpha = []
    alpha.append(AoA)
    vsp.SetDoubleAnalysisInput(analysis_name, "AlphaStart", alpha, 0)
    AlphaNpts = []
    vsp.SetIntAnalysisInput(analysis_name, "AlphaNpts", AlphaNpts, 0)
    mach = []
    mach.append(0.7)
    vsp.SetDoubleAnalysisInput(analysis_name, "MachStart", mach, 0)
    vsp.Update()
    #// list inputs, type, and current values
    vsp.PrintAnalysisInputs(analysis_name)
    print("")
    #// Execute
    print("\tExecuting...")
    rid = vsp.ExecAnalysis(analysis_name)
    print("COMPLETE")
    #// Get & Display Results
    #vsp.PrintResults( rid )
    history_res = vsp.FindLatestResultsID("VSPAERO_History")
    load_res = vsp.FindLatestResultsID("VSPAERO_Load")
    CL = vsp.GetDoubleResults(history_res, "CL", 0)
    cl = vsp.GetDoubleResults(load_res, "cl", 0)
    # ADDED TO CREATE A CSV FILE WITH NEEDED INFO
    vsp.WriteResultsCSVFile(rid, "z.csv")
    # Save and Export Vehicle --------------------------------------------------------------------------
    # Update the vehicle before saving/exporting
    vsp.Update()
    # Save to a file
    fname = "test_vehicle.vsp3"
    vsp.SetVSP3FileName(fname)
    print("\tSaving vehicle file to: ", fname)
    vsp.WriteVSPFile(vsp.GetVSPFileName(), vsp.SET_ALL)
    # Export STL
    fname = "test_vehicle_mesh.stl"
    print("\tExporting mesh (STL) as:", fname)
    mesh_id = vsp.ExportFile(fname, vsp.SET_ALL, vsp.EXPORT_STL)
    vsp.DeleteGeom(mesh_id) # Delete the mesh generated by the STL export
    #Run Mass Calc (for StabAnal)
    mesh_id = vsp.ComputeMassProps( vsp.SET_ALL, 20, vsp.X_DIR )
    mass_res_id = vsp.FindLatestResultsID( "Mass_Properties" )



ThickChord = 0.1
Camber = 0
CamberLoc = 0.2
TotalChord = 1.9
TotalSpan = 13.5
Twist = 0
AeroAnal(ThickChord, Camber, CamberLoc, TotalChord,  TotalSpan, Twist, 0)

def StabAnal(ThickChord, Camber, CamberLoc, TotalChord, TotalSpan, Twist):
    """
    Code to create an aircraft and run the stability analysis using the OpenVSP API.
    Takes aircraft paramaters as input
    Runs an aerodynamic analysis, and saves CSV file of coefficents
    MUST RUN AEROANAL() FIRST

    :param int ThickChord: Chord Thickness of the Airfoil
    :param Camber: Camber of the Airfoil
    :param CamberLoc: Location of the Camber on the Airfoil
    :param TotalChord: The Chord Length of the Wing
    :param TotalSpan: The Total Span of the Wing
    :param Twist: The Incidence Angle of the Wing
    :returns: The Static Margin
    """
    with open("z.csv") as f:
        reader = csv.reader(f)
        for i in range(28):
            row = next(reader)
        value = row[4-1]
    Cl1 = value
    
    with open("z.csv") as f:
        reader = csv.reader(f)
        for i in range(34):
            row = next(reader)
        value = row[4-1]
    Cmy1 = value
    
    AeroAnal(ThickChord, Camber, CamberLoc, TotalChord,  TotalSpan, Twist, 4)
    with open("z.csv") as f:
        reader = csv.reader(f)
        for i in range(28):
               row = next(reader)
        value = row[4-1]
    Cl2 = value
    with open("z.csv") as f:
        reader = csv.reader(f)
        for i in range(34):
            row = next(reader)
        value = row[4-1]
    Cmy2 = value
    xAc = (float(Cmy2)-float(Cmy1))/(float(Cl1)-float(Cl2)) #Aerodynamic Center
    with open("test_vehicle_MassProps.txt", "r") as f:
        rows = f.readlines()[20:21]
    rows = ''.join(rows)
    xCg = float(rows.split()[2]) #Center of Gravity
    SM = (xAc-xCg)/10 *100 #Static Margin
    return SM

print(StabAnal(ThickChord, Camber, CamberLoc, TotalChord, TotalSpan, Twist))