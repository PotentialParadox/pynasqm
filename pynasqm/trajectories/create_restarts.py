from functools import singledispatch
from pynasqm.utils import mkdir
from pynasqm.trajectories.qmground import QmGround
from pynasqm.trajectories.qmexcited import QmExcited
from pynasqm.trajectories.ppump import PPump
from pynasqm.trajectories.fluorescence import Fluorescence
from pynasqm.trajectories.start_from_mmground import start_from_mmground
from pynasqm.trajectories.start_from_qmground import start_from_qmground
from pynasqm.trajectories.snaps_from_parent import snaps_from_parent
from pynasqm.trajectories.start_from_restart import start_from_restart

@singledispatch
def create_restarts_from_parent(traj_data, restart, override):
    raise NotImplementedError("traj_data type not supported by create_restarts")


@create_restarts_from_parent.register(QmGround)
def _(traj_data, restart, override):
    create_directories(traj_data)
    if traj_data.user_input.restart_attempt == 0:
        start_from_mmground(traj_data)
    else:
        start_from_restart(traj_data, override)

@create_restarts_from_parent.register(QmExcited)
def _(traj_data, restart, override=False):
    create_directories(traj_data)
    if traj_data.user_input.restart_attempt == 0:
        start_from_qmground(traj_data, override)
    else:
        start_from_restart(traj_data, override)

@create_restarts_from_parent.register(PPump)
def _(traj_data, restart, override=False):
    create_directories(traj_data)
    start_from_qmground(traj_data, override)

@create_restarts_from_parent.register(Fluorescence)
def _(traj_data, restart, override=False):
    create_directories(traj_data)
    snaps_from_parent(traj_data)
    job = traj_data.job_suffix
    mkdir("{}".format(job))


def create_directories(traj_data):
    job = traj_data.job_suffix
    mkdir("{}".format(job))
    for i in range(1, traj_data.number_trajectories + 1):
        directory = "{}/traj_{}".format(job, i)
        restart_directory = "{}/traj_{}/restart_{}".format(job, i,
                                                           traj_data.user_input.restart_attempt)
        nmr_directory = "{}/traj_{}/nmr".format(job, i)
        mkdir(directory)
        mkdir(restart_directory)
        mkdir(nmr_directory)





