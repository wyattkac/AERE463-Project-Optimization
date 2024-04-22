from pyxdsm.XDSM import XDSM, OPT, FUNC, RIGHT

x= XDSM(use_sfmath=True)

x.add_system("opt", OPT, ("COBYLA", r"\text{openMDAO}"))
x.add_system("openvsp", FUNC, r"\text{OpenVSP}")
x.connect("opt","openvsp",[r"\text{Geometry Specs}"])
x.add_system("vspaero", FUNC, r"\text{VSPAero}")
x.add_input("vspaero", [r"\text{M}"])
x.connect("opt","vspaero",[r"\text{Re}"])
x.connect("openvsp", "vspaero", [r"\text{Mesh}"])
x.add_output("vspaero", [r"\text{Cl}",
                         r"\text{Cd}"])
x.connect("vspaero", "opt", [r"\text{Cl}",
                             r"\text{Cd}"])
x.add_system("stab", FUNC, r"\text{Stability}")
x.connect("vspaero", "stab", [r"\text{CP}"])
x.connect("openvsp", "stab", [r"\text{CG}"])
x.connect("stab","opt",[r"\text{Stability}"])
x.add_system("radar", FUNC, r"\text{RadarSimPy}")
x.connect("openvsp", "radar", [r"\text{Mesh}"])
x.add_output("radar", [r"\text{RCS}"])
x.connect("radar", "opt", [r"\text{RCS}"])

x.write("Actual_XDSM_Diagram")