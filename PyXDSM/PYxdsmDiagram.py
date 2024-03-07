from pyxdsm.XDSM import XDSM, FUNC, RIGHT

x= XDSM(use_sfmath=True)

x.add_system("openvsp", FUNC, r"\text{OpenVSP}")
x.add_input("openvsp", [r"\text{geometry}"])
x.add_system("vspaero", FUNC, r"\text{VSPAero}")
x.add_input("vspaero", [r"\text{velocity}",
                       r"\text{altitude}"])
x.connect("openvsp", "vspaero", [r"\text{mesh file}"])
x.add_output("vspaero", [r"\text{lift}",
                         r"\text{drag}"])
x.add_system("radar", FUNC, r"\text{RadarSimPy}")
x.connect("openvsp", "radar", [r"\text{mesh file}"])
x.add_output("radar", [r"\text{radar cross section}"])
x.write("xdsmDiagram")