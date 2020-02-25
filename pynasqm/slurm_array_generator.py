def generate_slurm_array(user_input, job_suffix):
    return array_from_ntrajs(user_input, job_suffix)

def get_number_trajectories(user_input, job_suffix):
    if job_suffix == "qmground":
        return user_input.n_snapshots_qmground
    if job_suffix == "qmexcited":
        return user_input.n_snapshots_ex
    if job_suffix == "abs":
        return user_input.n_snapshots_qmground


def array_from_ntrajs(user_input, job_suffix):
    ntrajs = get_number_trajectories(user_input, job_suffix)
    return f"1-{ntrajs}"
