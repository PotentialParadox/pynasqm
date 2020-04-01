import sys
from os import path

def generate_slurm_array(user_input, job_suffix):
    if should_read_from_file(user_input, job_suffix):
        return read_array_from_file(user_input, job_suffix)
    return array_from_ntrajs(user_input, job_suffix)

def get_number_trajectories(user_input, job_suffix):
    print(job_suffix)
    if job_suffix == "qmground":
        return user_input.n_snapshots_qmground
    if job_suffix == "qmexcited":
        return user_input.n_snapshots_ex
    if job_suffix == "absorption":
        return user_input.n_snapshots_qmground
    if job_suffix == "fluorescence":
        return user_input.n_snapshots_ex
    if job_suffix == "pulse_pump":
        return user_input.n_snapshots_ex

def should_read_from_file(user_input, job_suffix):
    filename =  get_filename(user_input, job_suffix)
    if filename == "":
        return False
    if path.exists(filename) == False:
        sys.exit(f"User requested to use trajectory file {filename}. But {filename} does not exist.")
    return True

def array_from_ntrajs(user_input, job_suffix):
    ntrajs = get_number_trajectories(user_input, job_suffix)
    return f"1-{ntrajs}"

def read_array_from_file(user_input, job_suffix):
    filename = get_filename(user_input, job_suffix)
    return (open(filename, 'r').read()).strip()

def get_filename(user_input, job_suffix):
    if job_suffix == "qmground":
        return user_input.qmground_traj_index_file
    if job_suffix == "qmexcited":
        return user_input.qmexcited_traj_index_file
    return ""

