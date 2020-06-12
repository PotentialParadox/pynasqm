from functools import singledispatch
from pynasqm.trajectories.qmground import QmGround
from pynasqm.trajectories.qmexcited import QmExcited
from pynasqm.trajectories.ppump import PPump
from pynasqm.trajectories.fluorescence import Fluorescence
from pynasqm.trajectories.absorption import Absorption
from pynasqm.trajectories.utils import traj_indices, snap_indices

@singledispatch
def select_working_directories(traj_data):
    raise NotImplementedError(f"traj_data type not supported by select_working_directories\n"\
                              f"{traj_data}")

@select_working_directories.register(QmGround)
@select_working_directories.register(QmExcited)
@select_working_directories.register(PPump)
def _(traj_data):
    restart = traj_data.user_input.restart_attempt
    job = traj_data.job_suffix
    return ["{}/traj_{}/restart_{}".format(job, traj, restart)
            for traj in traj_indices(traj_data)]

@select_working_directories.register(Fluorescence)
@select_working_directories.register(Absorption)
def _(traj_data):
    job = traj_data.job_suffix
    return [f"{job}/traj_{traj}/{snap_id}"
            for traj in traj_indices(traj_data)
            for snap_id in snap_indices(traj_data)]
