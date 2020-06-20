import os
import shutil
import numpy as np

def produce_coeff_string(coeffs):
    outputstring = ""
    for line in coeffs:
        outputstring += f"{int(line[0]):3d}"
        for coeff in line[1:]:
            outputstring += f"{coeff:20.10f}"
        outputstring += "\n"
    return outputstring

def collect_coeffs(number_trajectories, number_restarts):

    if os.path.isdir("coeffs"):
        shutil.rmtree("coeffs")
    os.mkdir("coeffs")

    for traj in range(1, number_trajectories + 1):
        src1 = f"qmexcited/traj_{traj}/restart_0/coeff-n.out"
        first_run_data = np.loadtxt(src1)
        first_time = first_run_data[1,1]
        last_time = first_run_data[-1,1]
        run_time = first_time + last_time

        total_data = first_run_data
        for restart in range(1, number_restarts+1):
            srcn = f"qmexcited/traj_{traj}/restart_{restart}/coeff-n.out"
            if not os.path.isfile(srcn):
                continue
            run_data = np.loadtxt(srcn)
            run_data[:, 1] = run_data[:, 1] + run_time*restart
            total_data = np.append(total_data, run_data, axis = 0)

        coeff_str = produce_coeff_string(total_data)

        dst = f"coeffs/coeff-{traj}.out"
        open(dst, 'w').write(coeff_str)
