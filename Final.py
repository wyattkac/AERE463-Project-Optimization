#!/usr/bin/env python
import subprocess, os, csv
import openmdao.api as om
import fileinput
import openvsp as vsp
import time
import shutil
from rcsFunc import rcs

__authors__ = "Wyatt, Nicholas"
__copyright__ = "Copyright 2024, Wyatt and Nicholas"
__status__ = "Prototype"

#TODO Add RCS
#TODO Add Structure
#TODO Add more inputs
#TODO Replace "Engine"
#TODO Clean Up Code (remove unneeded imports, tidy code & comments)

def AeroAnal(ThickChord, Camber, CamberLoc, TotalChord, TotalSpan, Twist, XLoc, AoA):
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
    vsp.SetParmVal(wing_id, "ThickChord", "XSecCurve_0", ThickChord[0]) #Range of 0 to 1
    vsp.SetParmVal(wing_id, "Camber", "XSecCurve_0", Camber[0]) #Range of 0 to 0.09
    vsp.SetParmVal(wing_id, "CamberLoc", "XSecCurve_0", CamberLoc[0]) #Range of 0.1 to 0.9
    #   Param for Wing
    vsp.SetParmVal(wing_id, "TotalChord", "WingGeom", TotalChord[0])
    #TODO
    #vsp.SetParmVal(wing_id, "Root_Chord", "XSec_1", 1.9)
    #TODO
    #vsp.SetParmVal(wing_id, "Tip_Chord", "XSec_1", 1.9)
    vsp.SetParmVal(wing_id, "TotalSpan", "WingGeom", TotalSpan[0])
    #TODO
    #vsp.SetParmVal(wing_id, "Sweep", "XSec_1", 10 ) #Range of -89 to 89
    vsp.SetParmVal(wing_id, "Twist", "XSec_0", Twist[0]) #Angle of Incidence
    #TODO
    vsp.SetParmVal(wing_id, "X_Rel_Location", "XForm", XLoc[0]) #Range of 0 to 10-Chord
    #   Params for Accuracy
    vsp.SetParmVal(wing_id, "SectTess_U", "XSec_1", 12) #Number of spanwise sections
    #vsp.SetParmVal(wing_id, "Density", "Mass_Props", 1)
    elev_id = vsp.AddGeom("WING", pod_id)
    vsp.SetParmVal(elev_id, "X_Rel_Location", "XForm", 8)
    #TODO
    vsp.SetParmVal(elev_id, "TotalArea", "WingGeom", .4*TotalChord[0]*(TotalSpan[0]*TotalChord[0])/(8.2-2.5))
    vsp.SetParmVal(elev_id, "SectTess_U", "XSec_1", 12)
    rudd_id = vsp.AddGeom("WING", pod_id)
    vsp.SetParmVal(rudd_id, "Sym_Planar_Flag", "Sym", 0.0 ) #Make it not symmetic (just half an airfoil)
    vsp.SetParmVal(rudd_id, "X_Rel_Rotation", "XForm", 90) #Rotate it vertically 
    vsp.SetParmVal(rudd_id, "X_Rel_Location", "XForm", 8.2)
    #TODO
    vsp.SetParmVal(rudd_id, "TotalArea", "WingGeom", .03*TotalSpan[0]*(TotalSpan[0]*TotalChord[0])/(8.2-2.5))
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

def StabAnal(ThickChord, Camber, CamberLoc, TotalChord, TotalSpan, Twist, XLoc, AoA):
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
    
    AeroAnal(ThickChord, Camber, CamberLoc, TotalChord,  TotalSpan, Twist, XLoc, AoA)
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
    

class AeroRCS_opt(om.ExplicitComponent):

    def setup(self):
        self.add_input("ThickChord", val=0.1)
        self.add_input("Camber", val=0.0)
        self.add_input("CamberLoc", val=0.2)
        self.add_input("TotalChord", val=1.9)
        self.add_input("TotalSpan", val=13.5)
        self.add_input("Twist", val=13.5)
        self.add_input("XLoc", val=0.0)

        self.add_output("Cl", val=0.0)
        self.add_output("Cd", val=0.0)
        self.add_output("Cd/Cl", val=0.0)
        self.add_output("SM", val=0.0)
        self.add_output("RCS", val=0.0)
        self.add_output("Tot_Obj", val=0.0)

    def setup_partials(self):
        # Finite difference all partials.
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs):
        ThickChord = inputs["ThickChord"]
        Camber = inputs["Camber"]
        CamberLoc = inputs["CamberLoc"]
        TotalChord = inputs["TotalChord"]
        TotalSpan = inputs["TotalSpan"]
        Twist = inputs["Twist"]
        XLoc = inputs["XLoc"]
        target = {
            "model": 'test_vehicle_mesh.stl',
            "location": (0, 0, 0),
        }

        AeroAnal(ThickChord, Camber, CamberLoc, TotalChord,  TotalSpan, Twist, XLoc, 4)
        outputs["SM"] = StabAnal(ThickChord, Camber, CamberLoc, TotalChord,  TotalSpan, Twist, XLoc, 0)
        [average_rcs, outputs["RCS"]] = rcs(target)

        with open("z.csv") as f:
            reader = csv.reader(f)
            for i in range(17):
                row = next(reader)
            value = row[4-1]
        outputs["Cd"] = value

        with open("z.csv") as f:
            reader = csv.reader(f)
            for i in range(28):
                row = next(reader)
            value = row[4-1]
        outputs["Cl"] = value
        
        outputs["Cd/Cl"] = outputs["Cd"] / outputs["Cl"]
        outputs["Tot_Obj"] = .5*outputs["Cd/Cl"] + .5*outputs["RCS"]

        print("ThickC ", ThickChord)
        print("Cam    ", Camber)
        print("CamL   ", CamberLoc)
        print("Chord  ", TotalChord)
        print("Span   ", TotalSpan)
        print("Twist  ", Twist)
        print("XLoc   ", XLoc)       
        print("Cl     ", outputs["Cl"])
        print("Cd/Cl  ", outputs["Cd/Cl"])
        myCsvRow = [ThickChord, Camber, CamberLoc, TotalChord, TotalSpan, Twist, XLoc, outputs["SM"], outputs["Cl"], outputs["Cd/Cl"], ]
        with open(r'x(hist).csv', 'a', newline='') as csvfile:
            fieldnames = ['1','2','3','4','5','6','7','8','9','10','11','12']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({'1':ThickChord, '2':Camber, '3':CamberLoc, '4':TotalChord, '5':TotalSpan, '6':Twist, '7':XLoc, '8':outputs["SM"], '9':outputs["Cl"], '10':outputs["Cd/Cl"], '11':outputs["RCS"], '12':outputs["Tot_Obj"]})
        #os.system('start cmd /c C:\\Users\\wyatt\\OneDrive\\Documents\\GitHub\\AERE463-Project-Optimization\\openFile.bat')
        #time.sleep(1)


if __name__ == "__main__":
    if os.path.exists("x(hist).csv"):
        shutil.copyfile('C:\\Users\\wyatt\\OneDrive\\Documents\\GitHub\\AERE463-Project-Optimization\\x(hist).csv', 'C:\\Users\\wyatt\\OneDrive\\Documents\\GitHub\\AERE463-Project-Optimization\\xxx(hist).csv')
        os.remove("x(hist).csv")
    else:
        print("No Hist File To Remove")
    
    with open(r'x(hist).csv', 'a', newline='') as csvfile:
        fieldnames = ['1','2','3','4','5','6','7','8','9','10','11','12']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({'1':'ThickChord', '2':'Camber', '3':'CamberLoc', '4':'TotalChord', '5':'TotalSpan', '6':'Twist', '7':'XLoc', '8':'outputs["SM"]', '9':'outputs["Cl"]', '10':'outputs["Cd/Cl"]', '11':'outputs["RCS"]', '12':'outputs["Tot_Obj"]'})

    model = om.Group()
    model.add_subsystem("engine", AeroRCS_opt())

    prob = om.Problem(model)
    
    prob.driver = om.SimpleGADriver()
    #prob.driver.options["maxiter"] = 20
    
    prob.model.add_design_var("engine.ThickChord", lower=.1, upper=1)
    prob.model.add_design_var("engine.Camber", lower=0, upper=0.9)
    prob.model.add_design_var("engine.CamberLoc", lower=0.1, upper=0.9)
    prob.model.add_design_var("engine.TotalChord", lower=1, upper=2)
    prob.model.add_design_var("engine.TotalSpan", lower=1, upper=15)
    prob.model.add_design_var("engine.Twist", lower=0, upper=5)
    prob.model.add_design_var("engine.XLoc", lower=0, upper=5)
    prob.model.add_constraint("engine.Cl", lower=0.3, upper=0.35)
    prob.model.add_constraint("engine.SM", lower=5, upper=25)
    prob.model.add_objective("engine.Tot_Obj", scaler=-100.0)
    
    prob.setup()
    
    prob.set_val("engine.ThickChord", 0.1)
    prob.set_val("engine.Camber", 0.0)
    prob.set_val("engine.CamberLoc", 0.2)
    prob.set_val("engine.TotalChord", 1.9)
    prob.set_val("engine.TotalSpan", 13.5)
    prob.set_val("engine.Twist", 0)
    prob.set_val("engine.XLoc", 2.5)
    
    prob.run_driver()
    
    f = prob.get_val("engine.Cd/Cl")
    Cl = prob.get_val("engine.mass_rate")
    print(Cl)
    print(f)
    