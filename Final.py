#!/usr/bin/env python
import subprocess, os, csv
import openmdao.api as om
import fileinput
import openvsp as vsp
import time
import shutil
from rcsFunc import rcs
from aeroFunc import AeroAnal, StabAnal

__authors__ = "Wyatt, Nicholas"
__copyright__ = "Copyright 2024, Wyatt and Nicholas"
__status__ = "Prototype"

#TODO Add Structure
#TODO Add more inputs
#TODO Clean Up Code (remove unneeded imports, tidy code & comments) 
   
generations = 10
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
        XLoc = 2.5
        target = {
            "model": 'test_vehicle_mesh.stl',
            "location": (0, 0, 0),
        }

        AeroAnal(ThickChord, Camber, CamberLoc, TotalChord,  TotalSpan, Twist, XLoc, 4)
        #outputs["SM"] = StabAnal(ThickChord, Camber, CamberLoc, TotalChord,  TotalSpan, Twist, XLoc, 0)
        #[average_rcs, outputs["max_RCS"]] = rcs(target)

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
        #outputs["Tot_Obj"] = .5*outputs["Cd/Cl"] + .5*outputs["max_RCS"]

        with open(r'x(hist).csv', 'a', newline='') as csvfile:
            fieldnames = ['1','2','3','4','5','6','7','8','9','10','11','12']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames,delimiter=',')
            writer.writerow({'1':float(ThickChord), '2':float(Camber), '3':float(CamberLoc), '4':float(TotalChord), '5':float(TotalSpan), '6':float(Twist), '7':float(XLoc), '8':"float(outputs["SM"]"), '9':float(outputs["Cl"]), '10':float(outputs["Cd/Cl"]), '11':"float(outputs["max_RCS"])", '12':"float(outputs["Tot_Obj"])"})
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
    
    prob.driver = om.SimpleGADriver()
    prob.driver.options["max_gen"] = generations
    
    prob.model.add_design_var("uav.ThickChord", lower=.1, upper=1)
    prob.model.add_design_var("uav.Camber", lower=0, upper=0.9)
    prob.model.add_design_var("uav.CamberLoc", lower=0.1, upper=0.9)
    prob.model.add_design_var("uav.TotalChord", lower=1, upper=2)
    prob.model.add_design_var("uav.TotalSpan", lower=1, upper=15)
    prob.model.add_design_var("uav.Twist", lower=0, upper=5)
    #prob.model.add_design_var("uav.XLoc", lower=0, upper=5)
    prob.model.add_constraint("uav.Cl", lower=0.3, upper=0.35)
    #prob.model.add_constraint("uav.SM", lower=5, upper=25)
    prob.model.add_objective("uav.Cd/Cl", scaler=-100.0)
    
    prob.setup()
    
    prob.set_val("uav.ThickChord", 0.1)
    prob.set_val("uav.Camber", 0.0)
    prob.set_val("uav.CamberLoc", 0.2)
    prob.set_val("uav.TotalChord", 1.9)
    prob.set_val("uav.TotalSpan", 13.5)
    prob.set_val("uav.Twist", 0)
    #prob.set_val("uav.XLoc", 2.5)
    
    prob.run_driver()
    