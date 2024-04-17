import subprocess, os
import openmdao.api as om
import fileinput



class RocketEngine(om.ExplicitComponent):

    def setup(self):
        self.add_input("chamber_pressure", val=0.0)
        self.add_input("mixture_ratio", val=0.0)
        self.add_input("throat_diameter", val=0.0)
        self.add_input("area_ratio", val=0.0)

        self.add_output("thrust", val=0.0)
        self.add_output("mass_rate", val=0.0)
        self.add_output("isp", val=0.0)

    def setup_partials(self):
        # Finite difference all partials.
        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs):
    
        cp = inputs["chamber_pressure"]
        mr = inputs["mixture_ratio"]
        td = inputs["throat_diameter"]
        ar = inputs["area_ratio"]
        
        os.chdir(r"C:\Users\phe\Desktop\rpa")
        
        idxI = 1
        for line in fileinput.input(files="my_engine.cfg", inplace=True, backup='.bak'):
            if idxI == 14:
                print("    value = %.8f;" % cp)
            elif idxI == 23:
                print("    areaRatio = %.8f;" % ar)
            elif idxI == 34:
                print("      value = %.8f;" % mr)
            elif idxI == 63:
                 print("    value = %.8f;" % td)
            else:
                print(line, end='')
            idxI += 1
        
        a = subprocess.Popen('rpas.exe -i my_engine.js', shell=True, stdout=subprocess.PIPE)
        b = a.stdout.read().decode("utf-8") # note the decode method

        for line in b.split("\n"):
            if "F = " in line:
                data = line.split(" ")
                outputs["thrust"] = float(data[2]) * 9.81
            if "m_dot = " in line:
                data = line.split(" ")
                outputs["mass_rate"] = float(data[2])
        
        outputs["isp"] = outputs["thrust"] / outputs["mass_rate"] / 9.81
        
        print("isp ", outputs["isp"])

if __name__ == "__main__":

    model = om.Group()
    model.add_subsystem("engine", RocketEngine())

    prob = om.Problem(model)
    
    prob.driver = om.ScipyOptimizeDriver()
    prob.driver.options["optimizer"] = "SLSQP"
    prob.driver.options["maxiter"] = 20
    
    prob.model.add_design_var("engine.chamber_pressure", lower=1, upper=8)
    prob.model.add_design_var("engine.mixture_ratio", lower=1, upper=20)
    prob.model.add_design_var("engine.throat_diameter", lower=0.01, upper=1)
    prob.model.add_design_var("engine.area_ratio", lower=1, upper=100)
    prob.model.add_constraint("engine.thrust", equals=100000)
    prob.model.add_objective("engine.isp", scaler=-1.0)
    
    prob.setup()
    
    prob.set_val("engine.chamber_pressure", 5.0)
    prob.set_val("engine.mixture_ratio", 3.5)
    prob.set_val("engine.throat_diameter", 0.13)
    prob.set_val("engine.area_ratio", 60)
    
    prob.run_driver()
    
    f = prob.get_val("engine.thrust")
    m_dot = prob.get_val("engine.mass_rate")
    isp = prob.get_val("engine.isp")
    cp = prob.get_val("engine.chamber_pressure")
    mr = prob.get_val("engine.mixture_ratio")
    td = prob.get_val("engine.throat_diameter")
    ar = prob.get_val("engine.area_ratio")
    print(cp, mr, td, ar)
    print(f, m_dot, isp)
    