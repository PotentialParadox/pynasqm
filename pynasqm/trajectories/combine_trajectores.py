import os

def combine_trajectories(suffix, n_trajs, n_runs):
    prmtop = "m1.prmtop"
    print ("-------- Combining Trajectories --------")
    if not os.path.isfile("m1.prmtop"):
        raise RuntimeError("m1.prmtop file not found while attempting to combine trajectories")
    for traj_id in range(1, n_trajs+1):
        combined = "combined" if iscombined(suffix, traj_id) else "uncombined"
        completed = "completed" if iscompleted(suffix, traj_id, n_runs) else "uncompleted"
        print ("Traj {} {} while previously {}".format(traj_id, completed, combined))
        if iscompleted(suffix, traj_id, n_runs):
            print("traj {} is completed".format(traj_id))
        else:
            print("traj {} is not completed".format(traj_id))
        if iscombined(suffix, traj_id):
            print("traj {} is already combined".format(traj_id))
        else:
            print("traj {} is not combined".format(traj_id))
        if iscompleted(suffix, traj_id, n_runs):
            init_frame = [f"{suffix}/traj_{traj_id}/restart_{restart}/snap_for_{suffix}_t{traj}_r{restart}.rst"]
            trajs = ["{}/traj_{}/restart_{}/nasqm_{}_t{}_r{}.nc".format(suffix, traj_id, restart,
                                                                        suffix, traj_id, restart)
                     for restart in range(n_runs)]
            traj = pt.load(init_frame + trajs, top=prmtop)
            pt.io.write_traj("{}/traj_{}/nasqm_{}_{}.nc".format(suffix, traj_id, suffix, traj_id),
                             traj, velocity=True, overwrite=True)
            subprocess.call(['rm'] + trajs)

def iscompleted(suffix, traj_id, n_runs):
    n_restarts = n_runs - 1
    restart_filename = "{}/traj_{}/restart_{}/snap_for_{}_t{}_r{}.rst".format(suffix, traj_id, n_restarts,
                                                                              suffix, traj_id, n_runs)
    traj_filename = "{}/traj_{}/restart_{}/nasqm_{}_t{}_r{}.nc".format(suffix, traj_id, n_restarts,
                                                                          suffix, traj_id, n_restarts)
    return os.path.isfile(restart_filename) and os.path.isfile(traj_filename)


def iscombined(suffix, traj_id):
    return os.path.isfile("{}/traj_{}/nasqm_{}_{}.nc".format(suffix, traj_id, suffix, traj_id))
