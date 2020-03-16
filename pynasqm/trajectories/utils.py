import os

def check_trajins(trajins):
    for trajin in trajins:
        if not os.path.isfile(trajin):
            raise RuntimeError(f"{trajin} was not found, make sure you ran the previous step: \n"\
                                f"mm_ground_state ->  qm_ground_state ->  absorption -> excited_state -> fluorescence\n"\
                                f"                                    -> pulse_pump \n")

def initial_snaps(traj_data):
    if traj_data.number_trajectories == 1:
        return ['{}'.format(traj_data.parent_restart_root)]
    return ["{}.{}".format(traj_data.parent_restart_root, x)
            for x in range(1, traj_data.number_trajectories + 1)]


def traj_indices(job_data):
    return range(1, job_data.number_trajectories+1)

def snap_indices(traj_data):
    return range(1, traj_data.n_snapshots_per_trajectory+1)
