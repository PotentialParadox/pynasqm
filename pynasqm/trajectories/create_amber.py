from pynasqm.amber import Amber
from pynasqm.trajectories.utils import traj_indices

def create_amber(traj_data):
    amber = Amber()
    roots = None
    restart_attempt = traj_data.user_input.restart_attempt
    if traj_data.user_input.is_hpc:
        roots = ["{}t${{ID}}_r{}".format(traj_data.child_root, restart_attempt)]
        restart_files = ["snap_for_{}_t${{ID}}_r{}.rst".format(traj_data.job_suffix, restart_attempt+1)]
        amber.prmtop_files = ["m1.prmtop"]
    else:
        roots = ["{}t{}_r{}".format(traj_data.child_root, i, restart_attempt)
                    for i in traj_indices(traj_data)]
        restart_files = ["snap_for_{}_t{}_r{}.rst".format(traj_data.job_suffix, i, restart_attempt+1)
                            for i in traj_indices(traj_data)]
        amber.prmtop_files = ["m1.prmtop"] * traj_data.number_trajectories
    amber.input_roots = roots
    amber.output_roots = roots
    amber.restart_files = restart_files
    amber.export_roots = roots
    amber.coordinate_files = coordinate_files(traj_data)
    amber.prmtop_files = prmtop_files(traj_data)
    amber.directories = output_directories(traj_data)
    return amber

def coordinate_files(traj_data):
    if traj_data.user_input.is_hpc:
        return hpc_coordinate_files(traj_data)
    return pc_coordinate_files(traj_data)

def prmtop_files(traj_data):
    if traj_data.user_input.is_hpc:
        return ["m1.prmtop"]
    return ["m1.prmtop"] * traj_data.number_trajectories

def output_directories(traj_data):
    restart = traj_data.user_input.restart_attempt
    job = traj_data.job_suffix
    return ["{}/traj_{}/restart_{}".format(job, traj, restart)
            for traj in traj_indices(traj_data)]

def hpc_coordinate_files(traj_data):
    return ["snap_for_{}_t${{ID}}_r{}.rst".format(traj_data.job_suffix,
                                                  traj_data.user_input.restart_attempt)]

def pc_coordinate_files(traj_data):
    return ["snap_for_{}_t{}_r{}.rst".format(traj_data.job_suffix, traj, traj_data.user_input.restart_attempt)
            for traj in traj_indices(traj_data)]
