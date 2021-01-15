from functools import singledispatch
from pynasqm.nasqmslurm  import slurm_trajectory_files
from pynasqm.trajectories.qmground import QmGround
from pynasqm.trajectories.qmexcited import QmExcited
from pynasqm.trajectories.fluorescence import Fluorescence
from pynasqm.trajectories.absorption import Absorption
from pynasqm.trajectories.ppump import PPump

def create_slurm(traj_data, amber):
    if traj_data.user_input.is_hpc:
        job_name = traj_data.user_input.job_name + traj_data.job_suffix
        directory = get_directory(traj_data)
        slurm_file = slurm_trajectory_files(traj_data.user_input,
                                            amber,
                                            job_name,
                                            traj_data.job_suffix,
                                            directory,
                                            traj_data.n_snapshots_per_trajectory)
    else:
        slurm_file = None
    return slurm_file

@singledispatch
def get_directory(traj_data):
    raise NotImplementedError(f"traj_data type not supported by create_slurm\n"\
                              f"{traj_data}")

@get_directory.register(QmGround)
@get_directory.register(QmExcited)
@get_directory.register(PPump)
def _(traj_data):
    return f"{traj_data.job_suffix}/traj_${{ID}}/restart_{traj_data.user_input.restart_attempt}"

@get_directory.register(Absorption)
@get_directory.register(Fluorescence)
def _(traj_data):
    return "{}/traj_${{ID}}/${{i}}".format(traj_data.job_suffix, traj_data.user_input.restart_attempt)
