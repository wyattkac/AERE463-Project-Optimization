# Type: Function

def rcs(target):
    import radarsimpy
    print('Running RadarSimPy...`)

    # %%
    import pymeshlab
    import numpy as np

    # target = {

    #         "model": 'C:/Users/Nicholas/Documents/ISU Spring 2024/AERE 463/AERE463-Project-Optimization/Example_Mesh1.stl',
    #         "location": (0, 0, 0),
    # }

    # # Simulate RCS vs Observation Angle
    # %%
    import time

    from radarsimpy.rt import rcs_sbr
    import numpy as np

    phi = np.arange(0, 180, 1)
    theta = 90
    freq = 3.1e9
    pol = [0, 0, 1]
    density = .1

    rcs = np.zeros_like(phi, dtype=float)

    tic = time.time()
    for phi_idx, phi_ang in enumerate(phi):
        rcs[phi_idx] = (
            rcs_sbr([target],
                    freq,
                    phi_ang,
                    theta,
                    pol=pol,
                    density=density))
    toc = time.time()

    print('Exec time :'+str(toc-tic) + 's')

    rcs = np.concatenate((rcs, rcs))
    phi = np.concatenate((phi, -phi))

    average_rcs = np.mean(rcs)
    # print(average_rcs)
    # with open('average_rcs.txt', 'a') as file:
    #     file.write(f"{average_rcs:.18f}\n")

    max_rcs = np.max(rcs)
    # print(max_rcs)
    # with open('max_rcs.txt', 'a') as file:
    #     file.write(f"{max_rcs:.18f}\n")
    return average_rcs, max_rcs
# if __name__ == '__main__':
#     # call func
#     RadarSimPy_Function()
