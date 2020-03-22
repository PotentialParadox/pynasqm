from pynasqm.nasqmslurm  import slurm_trajectory_files

def create_slurm(traj_data, amber):
    if traj_data.user_input.is_hpc:
        job_name = traj_data.user_input.job_name + traj_data.job_suffix
        directory = "{}/traj_${{ID}}/restart_{}".format(traj_data.job_suffix, traj_data.user_input.restart_attempt)
        slurm_file = slurm_trajectory_files(traj_data.user_input, amber,
                                            job_name, traj_data.job_suffix, directory)
    else:
        slurm_file = None
    return slurm_file
