import subprocess
from pynasqm.trajectories.combine_trajectores import combine_trajectories
from pynasqm.trajectories.utils import check_trajins, traj_indices, snap_indices
from pynasqm.cpptraj import create_restarts
from pynasqm.utils import mkdir

def snaps_from_parent(traj_data):
    combine_trajectories("qmexcited", traj_data.user_input.n_snapshots_ex, traj_data.user_input.n_exc_runs)
    qmexcited_trajs = [f"qmexcited/traj_{traj}/nasqm_qmexcited_{traj}.nc"
                       for traj in range(1, traj_data.number_trajectories+1)]
    outputs = [f"flu/traj_{traj}/qmexcited_t{traj}_snap" for traj in range(1, traj_data.number_trajectories+1)]
    check_trajins(qmexcited_trajs)
    restart_step = 1
    for trajin, output in zip(qmexcited_trajs, outputs):
        create_restarts(amber_inputfile=trajin, start=cpptraj_start_index(traj_data),
                        output=output, step=restart_step)
    move_restarts(traj_data)

def cpptraj_start_index(traj_data):
    n_frames = traj_data.number_frames_in_parent
    return n_frames - traj_data.n_snapshots_per_trajectory + 1

def move_restarts(traj_data):
    directories = [f"flu/traj_{traj}/{snap_id}"
                   for traj in traj_indices(traj_data)
                   for snap_id in snap_indices(traj_data)]
    for directory in directories:
        mkdir(directory)
    for inputfile, outputfile in zip(initial_snaps(traj_data), final_snaps(traj_data)):
        subprocess.call(['mv', inputfile, outputfile])

def initial_snaps(traj_data):
    if traj_data.n_snapshots_per_trajectory == 1:
        return [f'flu/traj_{traj}/qmexcited_t{traj}_snap'
                for traj in traj_indices(traj_data)]
    return [f'flu/traj_{traj}/qmexcited_t{traj}_snap.{snap_id}'
            for traj in traj_indices(traj_data)
            for snap_id in snap_indices(traj_data)]

def final_snaps(traj_data):
    if traj_data.n_snapshots_per_trajectory == 1:
        return [f'flu/traj_{traj}/1/snap_1_for_fluorescence_t{traj}.rst'
                for traj in traj_indices(traj_data)]
    return [f'flu/traj_{traj}/{snap_id}/snap_{snap_id}_for_fluorescence_t{traj}.rst'
            for traj in traj_indices(traj_data)
            for snap_id in snap_indices(traj_data)]

