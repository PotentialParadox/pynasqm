from pynasqm.utils import mkdir, copy_file, is_empty_file
from pynasqm.trajectories.utils import traj_indices
from pynasqm.trajectories.set_nexmd_seed import set_nexmd_seed
from pynasqm.trajectories.set_excited_states import set_excited_states

def create_inputceon_copies(traj_data):
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
