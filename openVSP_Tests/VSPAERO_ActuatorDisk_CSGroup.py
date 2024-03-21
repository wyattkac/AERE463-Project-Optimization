# Created by Justin Gravett, ESAero, 2/28/20
# Converted from C to Python by Wyatt Kacmarynski, 3/20/24
# Runs CFD using Vortex Lattice

import openvsp as vsp

def VSPAeroDiskAndCSGroupAnalysis():
    #//==== Create an example model ====//
    print("--> Generating Geometries")
    print("")

    pod_id = vsp.AddGeom("POD", "")
    wing_id = vsp.AddGeom("WING", pod_id)

    vsp.SetParmVal(wing_id, "X_Rel_Location", "XForm", 2.5)
    vsp.SetParmVal(wing_id, "TotalArea", "WingGeom", 25)
    vsp.SetParmVal(wing_id, "SectTess_U", "XSec_1", 12)

    #// Add a subsurface and create a control surface group
    subsurf_id = vsp.AddSubSurf(wing_id, vsp.SS_CONTROL, 0)

    group_index = vsp.CreateVSPAEROControlSurfaceGroup() #// Empty control surface group

    cs_group_name = "Example_CS_Group"
    vsp.SetVSPAEROControlGroupName(cs_group_name, group_index)

    available_cs_vec = vsp.GetAvailableCSNameVec(group_index)
    cs_index_vec = []
    cs_index_vec.append(1)
    cs_index_vec.append(2)
    #// Input cs_index_vec corresponds to the available control surfaces returned by GetAvailableCSNameVec
    vsp.AddSelectedToCSGroup( cs_index_vec, group_index ) #// cs_index_vec must be one based

    #// Check that the control surface was added to the group
    active_cs_vec = vsp.GetActiveCSNameVec( group_index )
    """
    if (active_cs_vec(0) != available_cs_vec(0)):
        print("ERROR: Available control surface not added to the group")
    """

    vsp.Update()

    #// Set the control surface deflections
    cs_group_container_id = vsp.FindContainer( "VSPAEROSettings", 0 )

    #// Set the gain on one side of the control surface positive and the other side negative
    #// for the overall deflection to be symmetric (pitch= vs roll moment)
    vsp.SetParmVal( vsp.FindParm( cs_group_container_id, "Surf_" + subsurf_id + "_0_Gain", "ControlSurfaceGroup_0" ), 1 )
    vsp.SetParmVal( vsp.FindParm( cs_group_container_id, "Surf_" + subsurf_id + "_1_Gain", "ControlSurfaceGroup_0" ), -1 )
    vsp.SetParmVal( vsp.FindParm( cs_group_container_id, "DeflectionAngle", "ControlSurfaceGroup_0" ), 10 ) #// degrees

    vsp.Update()

    #// Create an actuator disk
    prop_id = vsp.AddGeom( "PROP", pod_id )
    vsp.SetParmVal( prop_id, "PropMode", "Design", vsp.PROP_DISK )
    vsp.SetParmVal( prop_id, "Diameter", "Design", 6.0 )
    vsp.SetParmVal( prop_id, "X_Rel_Location", "XForm", -0.25 )

    vsp.Update()

    #// Setup the actuator disk VSPAERO parms
    disk_id = vsp.FindActuatorDisk( 0 )
    vsp.SetParmVal( vsp.FindParm( disk_id, "RotorRPM", "Rotor" ), 1234.0 )
    vsp.SetParmVal( vsp.FindParm( disk_id, "RotorCT", "Rotor" ), 0.35 )
    vsp.SetParmVal( vsp.FindParm( disk_id, "RotorCP", "Rotor" ), 0.55 )
    vsp.SetParmVal( vsp.FindParm( disk_id, "RotorHubDiameter", "Rotor" ), 1.0 )

    vsp.Update()

    #//==== Setup export filenames ====//
    fname_vspaerotests = "VSPAero_Disk.vsp3"

    #//==== Save Vehicle to File ====//
    print( "-->Saving vehicle file to: ")
    print( fname_vspaerotests)
    print( "" )
    vsp.WriteVSPFile( fname_vspaerotests, vsp.SET_ALL )
    print( "COMPLETE\n" )
    vsp.Update()

    #//==== Analysis: VSPAero Compute Geometry to Create Vortex Lattice DegenGeom File ====//
    compgeom_name = "VSPAEROComputeGeometry"
    print( compgeom_name )

    #// Set defaults
    vsp.SetAnalysisInputDefaults( compgeom_name )
    
    #// Analysis method
    analysis_method = list(vsp.GetIntAnalysisInput( compgeom_name, "AnalysisMethod" ))
    analysis_method[0] = vsp.VORTEX_LATTICE
    vsp.SetIntAnalysisInput( compgeom_name, "AnalysisMethod", analysis_method )

    #// list inputs, type, and current values
    vsp.PrintAnalysisInputs( compgeom_name )

    #// Execute
    print( "\tExecuting..." )
    compgeom_resid = vsp.ExecAnalysis( compgeom_name )
    print( "COMPLETE" )

    #// Get & Display Results
    vsp.PrintResults( compgeom_resid )

    #//==== Analysis: VSPAero Sweep ====//
    analysis_name = "VSPAEROSweep"

    vsp.SetAnalysisInputDefaults( analysis_name )

    #// Reference geometry set
    geom_set = []
    geom_set.append( 0 )
    vsp.SetIntAnalysisInput( analysis_name, "GeomSet", geom_set, 0 )
    ref_flag = []
    ref_flag.append( 1 )
    vsp.SetIntAnalysisInput( analysis_name, "RefFlag", ref_flag, 0 )
    wid = vsp.FindGeomsWithName( "WingGeom" )
    vsp.SetStringAnalysisInput( analysis_name, "WingID", wid, 0 )

    #// Freestream Parameters
    alpha = []
    alpha.append( 0.0 )
    vsp.SetDoubleAnalysisInput( analysis_name, "AlphaStart", alpha, 0 )
    AlphaNpts = []
    vsp.SetIntAnalysisInput( analysis_name, "AlphaNpts", AlphaNpts, 0)
    mach = []
    mach.append( 0.1 )
    vsp.SetDoubleAnalysisInput( analysis_name, "MachStart", mach, 0 )

    vsp.Update()

    #// list inputs, type, and current values
    vsp.PrintAnalysisInputs( analysis_name )
    print( "" )

    #// Execute
    print( "\tExecuting..." )
    rid = vsp.ExecAnalysis( analysis_name )
    print( "COMPLETE" )

    #// Get & Display Results
    vsp.PrintResults( rid )

    history_res = vsp.FindLatestResultsID( "VSPAERO_History" )
    load_res = vsp.FindLatestResultsID( "VSPAERO_Load" )

    CL = vsp.GetDoubleResults( history_res, "CL", 0 )
    cl = vsp.GetDoubleResults( load_res, "cl", 0 )

    # ADDED TO CREATE A CSV FILE WITH NEEDED INFO
    vsp.WriteResultsCSVFile( rid, "z.csv" )

print("Begin VSPAERO Actuator Disk & Control Surface Group Analysis")
print( "" )

VSPAeroDiskAndCSGroupAnalysis()

print("End VSPAERO Actuator Disk & Control Surface Group Analysis")