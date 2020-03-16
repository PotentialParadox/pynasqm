from functools import singledispatch
from pynasqm.utils import mkdir, copy_file, is_empty_file
from pynasqm.trajectories.qmground import QmGround
from pynasqm.trajectories.qmexcited import QmExcited
from pynasqm.trajectories.fluorescence import Fluorescence
from pynasqm.trajectories.absorption import Absorption
from pynasqm.trajectories.ppump import PPump
from pynasqm.trajectories.utils import traj_indices, snap_indices
from pynasqm.trajectories.set_nexmd_seed import set_nexmd_seed
from pynasqm.trajectories.set_excited_states import set_excited_states

@singledispatch
def create_inputceon_copies(traj_data):
    raise NotImplementedError(
        f"Create InputCeon Copies not Implemented for this data type\n"\
        f"{traj_data}"
    )

@create_inputceon_copies.register(QmGround)
@create_inputceon_copies.register(QmExcited)
@create_inputceon_copies.register(PPump)
def _(traj_data):
    inputceons = []
    attempt = traj_data.user_input.restart_attempt
    job = traj_data.job_suffix
    mkdir("{}".format(job))
    for index in traj_indices(traj_data):
        file_name = "{}t{}_r{}.in".format(traj_data.child_root, index, attempt)
        mkdir("{}/traj_{}".format(job, index))
        mkdir("{}/traj_{}/restart_{}".format(job, index, attempt))
        directory = "{}/traj_{}/restart_{}".format(job, index, attempt)
        inputceons.append(traj_data.input_ceons[0].copy(directory, file_name))
    inputceons = set_nexmd_seed(traj_data, inputceons)
    inputceons = set_excited_states(traj_data, inputceons)
    traj_data.input_ceons = inputceons

@create_inputceon_copies.register(Fluorescence)
@create_inputceon_copies.register(Absorption)
def _(traj_data):
    inputceons = []
    attempt = traj_data.user_input.restart_attempt
    job = traj_data.job_suffix
    directories = [f"{job}/traj_{traj}/{snap_id}"
                   for traj in traj_indices(traj_data)
                   for snap_id in snap_indices(traj_data)]
    file_names = [f"nasqm_{job}_t{traj}_{snap_id}.in"
                  for traj in traj_indices(traj_data)
                  for snap_id in snap_indices(traj_data)]
    for directory, file_name in zip(directories, file_names):
        mkdir(directory)
        inputceons.append(traj_data.input_ceons[0].copy(directory, file_name))
    inputceons = set_nexmd_seed(traj_data, inputceons)
    inputceons = set_excited_states(traj_data, inputceons)
    traj_data.input_ceons = inputceons
