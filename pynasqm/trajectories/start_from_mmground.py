from pynasqm.trajectories.check_trajins import check_trajins
from pynasqm.trajectories.utils import initial_snaps
from pynasqm.trajectories.extract_snaps_from_trajectory import extract_snaps_from_trajectory
import subprocess

def start_from_mmground(traj_data):
    mm_trajs = [f"mmground/restart_{r}/nasqm_ground_r{r}.nc" for r in range(traj_data.user_input.n_ground_runs)]
    check_trajins(traj_data, mm_trajs)
    restart_step = int(traj_data.number_frames_in_parent / traj_data.number_trajectories)
    extract_snaps_from_trajectory(trajectory_files=mm_trajs,
                                    output=traj_data.parent_restart_root, step=restart_step)
    move_restarts(traj_data)

def move_restarts(traj_data):
    for i, filename in enumerate(initial_snaps(traj_data), start=1):
        new_resart_name = "snap_for_qmground_t{}_r{}.rst".format(i, traj_data.user_input.restart_attempt)
        directory = "qmground/traj_{}/restart_{}/{}".format(i, traj_data.user_input.restart_attempt, new_resart_name)
        subprocess.call(['mv', filename, directory])
