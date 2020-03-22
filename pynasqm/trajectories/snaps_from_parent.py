import subprocess
from functools import singledispatch
from pynasqm.trajectories.combine_trajectores import combine_trajectories
from pynasqm.trajectories.utils import check_trajins, traj_indices, snap_indices
from pynasqm.cpptraj import create_restarts
from pynasqm.utils import mkdir
from pynasqm.trajectories.fluorescence import Fluorescence
from pynasqm.trajectories.absorption import Absorption

def snaps_from_parent(traj_data):
    ref_job = get_reference_job(traj_data)
    job = traj_data.job_suffix
    n_ref_trajs = get_n_trajs_of_reference(traj_data)
    n_ref_runs = get_n_ref_runs(traj_data)
    combine_trajectories(ref_job, n_ref_trajs, n_ref_runs)
    ref_trajs = [f"{ref_job}/traj_{traj}/nasqm_{ref_job}_{traj}.nc"
                       for traj in range(1, traj_data.number_trajectories+1)]
    outputs = [f"{job}/traj_{traj}/{ref_job}_t{traj}_snap" for traj in range(1, traj_data.number_trajectories+1)]
    check_trajins(ref_trajs)
    restart_step = 1
    for trajin, output in zip(ref_trajs, outputs):
        create_restarts(amber_inputfile=trajin, start=cpptraj_start_index(traj_data),
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

@singledispatch
def get_reference_job(traj_data):
    raise NotImplementedError(f"traj_data type not supported by get_refer\n"\
                              f"{traj_data}")
@get_reference_job.register(Fluorescence)
def _(traj_data):
    return "qmexcited"
@get_reference_job.register(Absorption)
def _(traj_data):
    return "qmground"

@singledispatch
def get_n_trajs_of_reference(traj_data):
    raise NotImplementedError(f"traj_data type not supported by get_ntrajs_of_reference\n"\
                              f"{traj_data}")
@get_n_trajs_of_reference.register(Fluorescence)
def _(traj_data):
    return traj_data.user_input.n_snapshots_ex
@get_n_trajs_of_reference.register(Absorption)
def _(traj_data):
    return traj_data.user_input.n_snapshots_qmground

@singledispatch
def get_n_ref_runs(traj_data):
    raise NotImplementedError(f"traj_data type not supported by get_nref_runs\n"\
                              f"{traj_data}")
@get_n_ref_runs.register(Fluorescence)
def _(traj_data):
    return traj_data.user_input.n_exc_runs
@get_n_ref_runs.register(Absorption)
def _(traj_data):
    return traj_data.user_input.n_qmground_runs



