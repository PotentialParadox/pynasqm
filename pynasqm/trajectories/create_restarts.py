from functools import singledispatch
from pynasqm.utils import mkdir
from pynasqm.trajectories.qmground import QmGround
from pynasqm.trajectories.start_from_mmground import start_from_mmground
from pynasqm.trajectories.start_from_restart import start_from_restart

@singledispatch
def create_restarts_from_parent(traj_data, restart, override):
    raise NotImplementedError("traj_data type not supported by create_restarts")


@create_restarts_from_parent.register(QmGround)
def create_restarts_from_parent(traj_data, restart, override):
    create_directories(traj_data)
    if traj_data.user_input.restart_attempt == 0:
        start_from_mmground(traj_data)
    else:
        start_from_restart(traj_data, override)


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





