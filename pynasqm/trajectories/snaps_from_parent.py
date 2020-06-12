import subprocess
from pynasqm.trajectories.combine_trajectores import combine_trajectories
from pynasqm.trajectories.utils import traj_indices, snap_indices
from pynasqm.trajectories.check_trajins import check_trajins
from pynasqm.cpptraj import create_restarts
from pynasqm.utils import mkdir
from pynasqm.trajectories.fluorescence import Fluorescence
from pynasqm.trajectories.absorption import Absorption
from pynasqm.trajectories.get_reference_job import get_reference_job
from pynasqm.trajectories.get_reference_job import get_n_trajs_of_reference
from pynasqm.trajectories.get_reference_job import get_n_ref_runs

def snaps_from_parent(traj_data):
    ref_job = get_reference_job(traj_data)
    job = traj_data.job_suffix
    n_ref_trajs = get_n_trajs_of_reference(traj_data)
    n_ref_runs = get_n_ref_runs(traj_data)
    combine_trajectories(ref_job, n_ref_trajs, n_ref_runs)
    ref_trajs = [(traj, f"{ref_job}/traj_{traj}/nasqm_{ref_job}_{traj}.nc")
                       for traj in range(1, traj_data.number_trajectories+1)]
    ref_trajs = check_trajins(traj_data, ref_trajs)
    outputs = [f"{job}/traj_{traj}/{ref_job}_t{traj}_snap" for (traj, _) in ref_trajs]
    restart_step = 1
    for trajin, output in zip(ref_trajs, outputs):
        create_restarts(amber_inputfile=trajin[1], start=cpptraj_start_index(traj_data),
                        output=output, step=restart_step)
    move_restarts(traj_data, job, ref_job)

def cpptraj_start_index(traj_data):
    n_frames = traj_data.number_frames_in_parent
    return n_frames - traj_data.n_snapshots_per_trajectory + 1

def move_restarts(traj_data, job, ref_job):
    directories = [f"{job}/traj_{traj}/{snap_id}"
                   for traj in traj_indices(traj_data)
                   for snap_id in snap_indices(traj_data)]
    for directory in directories:
        mkdir(directory)
    for inputfile, outputfile in zip(initial_snaps(traj_data, job, ref_job),
                                     final_snaps(traj_data, job)):
        subprocess.call(['mv', inputfile, outputfile])

def initial_snaps(traj_data, job, ref_job):
    if traj_data.n_snapshots_per_trajectory == 1:
        return [f'{job}/traj_{traj}/{ref_job}_t{traj}_snap'
                for traj in traj_indices(traj_data)]
    return [f'{job}/traj_{traj}/{ref_job}_t{traj}_snap.{snap_id}'
            for traj in traj_indices(traj_data)
            for snap_id in snap_indices(traj_data)]

def final_snaps(traj_data, job):
    if traj_data.n_snapshots_per_trajectory == 1:
        return [f'{job}/traj_{traj}/1/snap_1_for_{job}_t{traj}.rst'
                for traj in traj_indices(traj_data)]
    return [f'{job}/traj_{traj}/{snap_id}/snap_{snap_id}_for_{job}_t{traj}.rst'
            for traj in traj_indices(traj_data)
            for snap_id in snap_indices(traj_data)]





