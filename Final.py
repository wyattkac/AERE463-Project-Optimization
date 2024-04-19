#!/usr/bin/env python
import subprocess, os, csv
import openmdao.api as om
import fileinput
import openvsp as vsp
import time
import shutil
from rcsFunc import rcs
from aeroFunc import AeroAnal, StabAnal
import math

__authors__ = "Wyatt, Nicholas"
__copyright__ = "Copyright 2024, Wyatt and Nicholas"
__status__ = "Prototype"

#TODO Add Structure
#TODO Add more inputs
#TODO Clean Up Code (remove unneeded imports, tidy code & comments) 

generations = 10
cl_max = .1
cl_min = .05
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
        #self.add_output("SM", val=0.0)
        #self.add_output("max_RCS", val=0.0)
        #self.add_output("Tot_Obj", val=0.0)

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
        XLoc = [2.5]
        target = {
            "model": 'test_vehicle_mesh.stl',
            "location": (0, 0, 0),
        }

        AeroAnal(ThickChord, Camber, CamberLoc, TotalChord,  TotalSpan, Twist, XLoc, 4)
        #outputs["SM"] = StabAnal(ThickChord, Camber, CamberLoc, TotalChord,  TotalSpan, Twist, XLoc, 0)
        #[average_rcs, outputs["max_RCS"]] = rcs(target)

        with open("z.csv") as f:
            reader = csv.reader(f)
            for i in range(18): #Use Cdtott instead because Cdtot was creating negative numbers (Cdi was negative)
                row = next(reader)
            value = row[6-1]
        outputs["Cd"] = value

        with open("z.csv") as f:
            reader = csv.reader(f)
            for i in range(28):
                row = next(reader)
            value = row[6-1]
        outputs["Cl"] = value
        
        outputs["Cd/Cl"] = outputs["Cd"] / outputs["Cl"]
        if(float(outputs["Cl"])>cl_max):
            outputs["Cd/Cl"] = float(outputs["Cd/Cl"]) + 1000000*(float(outputs["Cl"])-cl_max)
        elif(float(outputs["Cl"])<cl_min):
            outputs["Cd/Cl"] = float(outputs["Cd/Cl"]) + 1000000*(cl_min-float(outputs["Cl"]))

        #if(float(outputs["Cd/Cl"]) < 0):
        #    outputs["Cd/Cl"] = 100
        #outputs["Tot_Obj"] = .5*outputs["Cd/Cl"] + .5*outputs["max_RCS"]

        with open(r'x(hist).csv', 'a', newline='') as csvfile:
            fieldnames = ['1','2','3','4','5','6','7','8','9','10','11','12']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames,delimiter=',')
            writer.writerow({'1':float(ThickChord), '2':float(Camber), '3':float(CamberLoc), '4':float(TotalChord), '5':float(TotalSpan), '6':float(Twist), '7':XLoc, '8':"float(outputs[\"SM\"])", '9':float(outputs["Cl"]), '10':float(outputs["Cd/Cl"]), '11':"float(outputs[\"max_RCS\"])", '12':"float(outputs[\"Tot_Obj\"])"})
        #os.system('start cmd /c C:\\Users\\wyatt\\OneDrive\\Documents\\GitHub\\AERE463-Project-Optimization\\openFile.bat')
        #time.sleep(1)


if __name__ == "__main__":
    if os.path.exists("x(hist).csv"):
        shutil.copy2('x(hist).csv', 'xxx(hist).csv')
        os.remove("x(hist).csv")
    else:
        print("No Hist File To Remove")
    
    with open(r'x(hist).csv', 'a', newline='') as csvfile:
        fieldnames = ['1','2','3','4','5','6','7','8','9','10','11','12']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',')
        writer.writerow({'1':'ThickChord', '2':'Camber', '3':'CamberLoc', '4':'TotalChord', '5':'TotalSpan', '6':'Twist', '7':'XLoc', '8':'outputs["SM"]', '9':'outputs["Cl"]', '10':'outputs["Cd/Cl"]', '11':'outputs["max_RCS"]', '12':'outputs["Tot_Obj"]'},)

    model = om.Group()
    model.add_subsystem("uav", AeroRCS_opt())

    prob = om.Problem(model)
    
    prob.driver = om.ScipyOptimizeDriver()
    prob.driver.options["optimizer"] = "COBYLA" #COBYLA or SLSQP
    #prob.driver.options['maxiter'] = 200
    #prob.driver = om.DOEDriver(om.LatinHypercubeGenerator())
    #prob.driver = om.DifferentialEvolutionDriver()
    #prob.driver.options["max_gen"] = generations
    #prob.driver.options['Pc'] = 0.5
    #prob.driver.options['F'] = 0.5
    
    prob.model.add_design_var("uav.ThickChord", lower=0.05, upper=0.2)
    prob.model.add_design_var("uav.Camber", lower=0.01, upper=0.09)
    prob.model.add_design_var("uav.CamberLoc", lower=0.1, upper=0.5)
    prob.model.add_design_var("uav.TotalChord", lower=1.0, upper=3.0)
    prob.model.add_design_var("uav.TotalSpan", lower=5.0, upper=15.0)
    prob.model.add_design_var("uav.Twist", lower=0.0, upper=5.0)
    #prob.model.add_design_var("uav.XLoc", lower=0, upper=5)
    prob.model.add_constraint("uav.Cl", lower=cl_min, upper=cl_max) #Manually added with penalty method
    #prob.model.add_constraint("uav.SM", lower=5, upper=25)
    prob.model.add_objective("uav.Cd/Cl")
    
    prob.setup()
    
    prob.set_val("uav.ThickChord", 0.05) #0.1
    prob.set_val("uav.Camber", 0.09) #0.0
    prob.set_val("uav.CamberLoc", 0.5) #0.2
    prob.set_val("uav.TotalChord", 1.1) #1.9
    prob.set_val("uav.TotalSpan", 13.99) #13.5
    prob.set_val("uav.Twist", 0.35) #0.0
    #prob.set_val("uav.XLoc", 2.5)
    
    prob.run_driver()

    print("ThickChord ", prob.get_val("uav.ThickChord"))
    print("Camber     ", prob.get_val("uav.Camber"))
    print("CamberLoc  ", prob.get_val("uav.CamberLoc"))
    print("Chord      ", prob.get_val("uav.TotalChord"))
    print("Span       ", prob.get_val("uav.TotalSpan"))
    print("Twist      ", prob.get_val("uav.Twist"))
    #print("XLoc       ", prob.get_val("uav.XLoc"))
    print("Cl         ", prob.get_val("uav.Cl"))
    print("Cd/Cl      ", prob.get_val("uav.Cd/Cl"))
    