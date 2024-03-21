# Part of the Master_VSP_VV_Script converted into Python to learn how to use the panel method solver
# NOT WORKING
# TODO ALL
import openvsp as vsp

#Lines 3065-3123
"""
#//==== Analysis: VSPAero Panel Single ====//
            print( m_VSPSweepAnalysis );
            
#//==== Analysis: VSPAero Compute Geometry to Create Vortex Lattice DegenGeom File ====//
            print(m_CompGeomAnalysis)

#// Set defaults
            vsp.SetAnalysisInputDefaults( m_CompGeomAnalysis );
            
            array<int> panel_analysis(1, VSPAERO_ANALYSIS_METHOD::PANEL);
            vsp.SetIntAnalysisInput( m_CompGeomAnalysis, "AnalysisMethod", panel_analysis );
            
            vsp.SetIntAnalysisInput(m_CompGeomAnalysis, "Symmetry", m_SymFlagVec, 0);

#// list inputs, type, and current values
            vsp.PrintAnalysisInputs( m_CompGeomAnalysis )

#// Execute
print( "\tExecuting..." )
compgeom_resid = vsp.ExecAnalysis(m_CompGeomAnalysis)
print( "COMPLETE" )

#// Get & Display Results
vsp.PrintResults( compgeom_resid )
"""

wid = vsp.AddGeom("WING", "")
m_VSPSweepAnalysis = "VSPAEROSweep"
m_GeomVec = [0] #// Set: All
m_RefFlagVec = [1] #// Wing Reference
m_WakeIterVec = [3]
m_SymFlagVec = [1]
panel_analysis = [vsp.PANEL]
AlphaNpts = [1]
m_MachVec = [.5]
MachNpts = [1,1]
fname_res_pm = "z_test_pm_res.csv"
#//==== Analysis: VSPAero Panel Single ====//
#// Set defaults
vsp.SetAnalysisInputDefaults(m_VSPSweepAnalysis)
print(m_VSPSweepAnalysis)

#// Reference geometry set
vsp.SetIntAnalysisInput(m_VSPSweepAnalysis, "GeomSet", m_GeomVec, 0)
vsp.SetIntAnalysisInput(m_VSPSweepAnalysis, "RefFlag", m_RefFlagVec, 0)
vsp.SetStringAnalysisInput(m_VSPSweepAnalysis, "WingID", wid, 0)
vsp.SetIntAnalysisInput(m_VSPSweepAnalysis, "WakeNumIter", m_WakeIterVec, 0)
vsp.SetIntAnalysisInput( m_VSPSweepAnalysis, "AnalysisMethod", panel_analysis )
vsp.SetIntAnalysisInput(m_VSPSweepAnalysis, "Symmetry", m_SymFlagVec, 0)

#// Freestream Parameters
Alpha = [1.0]
vsp.SetDoubleAnalysisInput(m_VSPSweepAnalysis, "AlphaStart", Alpha, 0)
vsp.SetIntAnalysisInput(m_VSPSweepAnalysis, "AlphaNpts", AlphaNpts, 0)
vsp.SetDoubleAnalysisInput(m_VSPSweepAnalysis, "MachStart", m_MachVec, 0)
vsp.SetIntAnalysisInput(m_VSPSweepAnalysis, "MachNpts", MachNpts, 0)

vsp.Update()

#// list inputs, type, and current values
vsp.PrintAnalysisInputs( m_VSPSweepAnalysis )
print( "" )

#// Execute
print( "\tExecuting..." )
rid = vsp.ExecAnalysis( m_VSPSweepAnalysis )
print( "COMPLETE" )

#// Get & Display Results
vsp.PrintResults( rid )
vsp.WriteResultsCSVFile( rid, fname_res_pm )
