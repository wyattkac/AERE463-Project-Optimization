# Part of the TestAnalysisVSPAERO converted into Python to learn how to use the panel method solver
# CONTAINS ONLY PANEL METHOD GEOMETRY SOLVER
import openvsp as vsp

def GenerateGeom():
    #//==== Create some test geometries ====//
    print("--> Generating Geometries")
    print("")

    pod_id = vsp.AddGeom("POD", "")
    wing_id = vsp.AddGeom("WING", "")

    vsp.SetParmVal( wing_id, "X_Rel_Location", "XForm", 2.5 )
    vsp.SetParmVal( wing_id, "TotalArea", "WingGeom", 25 )

    subsurf_id = vsp.AddSubSurf( wing_id, vsp.SS_CONTROL, 0 )

    vsp.Update()

    #//==== Setup export filenames ====//
    fname_vspaerotests = "TestVSPAero.vsp3"

    #//==== Save Vehicle to File ====//
    print("-->Saving vehicle file to: ")
    print(fname_vspaerotests)
    print("")
    vsp.WriteVSPFile(fname_vspaerotests, vsp.SET_ALL)
    print("COMPLETE\n")
    vsp.Update()

def TestVSPAeroComputeGeomPanel():
    print("-> Begin TestVSPAeroComputeGeomPanel")
    print("")

    #//open the file created in GenerateGeom
    fname_vspaerotests = "TestVSPAero.vsp3"
    vsp.ReadVSPFile(fname_vspaerotests)  #// Sets VSP3 file name

    #//==== Analysis: VSPAero Compute Geometry ====//
    analysis_name = "VSPAEROComputeGeometry"
    print(analysis_name)

    #// Set defaults
    vsp.SetAnalysisInputDefaults(analysis_name)

    #// Set to panel method
    analysis_method = list(vsp.GetIntAnalysisInput( analysis_name, "AnalysisMethod" ))
    analysis_method[0] = vsp.PANEL
    vsp.SetIntAnalysisInput(analysis_name, "AnalysisMethod", analysis_method)

    #// list inputs, type, and current values
    vsp.PrintAnalysisInputs(analysis_name)
    print("")

    #// Execute
    print("\tExecuting...")
    rid = vsp.ExecAnalysis( analysis_name )
    print("COMPLETE")

    #// Get & Display Results
    vsp.PrintResults( rid )

    # ADDED TO CREATE A CSV FILE WITH NEEDED INFO
    vsp.WriteResultsCSVFile( rid, "z.csv" )

#//==== Panel Method ====//
GenerateGeom()
TestVSPAeroComputeGeomPanel()
