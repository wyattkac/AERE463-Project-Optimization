import openmdao.api as om
import pygad

# build the model
prob = om.Problem()

prob.model.add_subsystem('paraboloid', om.ExecComp('f = (x-3)**2 + x*y + (y+4)**2 - 3'))

# setup the optimization
#prob.driver = om.ScipyOptimizeDriver()
#prob.driver.options['optimizer'] = 'SLSQP'
prob.driver = om.SimpleGADriver()

prob.model.add_design_var('paraboloid.x', lower=-50, upper=50)
prob.model.add_design_var('paraboloid.y', lower=-50, upper=50)
prob.model.add_objective('paraboloid.f')

prob.setup()

# Set initial values.
prob.set_val('paraboloid.x', 3.0)
prob.set_val('paraboloid.y', -4.0)

# run the optimization
prob.run_driver()

if prob.comm.rank == 0:
    print("\nOptimal Solution:")
    print(f"{prob.get_val('paraboloid.f')=}")
    print(prob.driver.iter_count)