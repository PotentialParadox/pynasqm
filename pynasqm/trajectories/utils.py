
def initial_snaps(traj_data):
    if traj_data.number_trajectories == 1:
        return ['{}'.format(traj_data.parent_restart_root)]
    return ["{}.{}".format(traj_data.parent_restart_root, x)
            for x in range(1, traj_data.number_trajectories + 1)]


def traj_indices(job_data):
    return range(1, job_data.number_trajectories+1)

def snap_indices(traj_data):
    return range(1, traj_data.n_snapshots_per_trajectory+1)
