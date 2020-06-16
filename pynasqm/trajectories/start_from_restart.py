import os
from pynasqm.utils import mkdir, copy_file, is_empty_file
from pynasqm.trajectories.create_restarts import test1
# from pynasqm.trajectories.create_restarts import create_restarts

def start_from_restart(job_data, override):
    restart = job_data.user_input.restart_attempt
    job = job_data.job_suffix
    for traj in range(1, job_data.number_trajectories+1):
        source_path = "{}/traj_{}/restart_{}/snap_for_{}_t{}_r{}.rst".format(job, traj,
                                                                                restart-1,
                                                                                job,
                                                                                traj,
                                                                                restart)
        output_path = "{}/traj_{}/restart_{}/snap_for_{}_t{}_r{}.rst".format(job, traj,
                                                                                restart,
                                                                                job,
                                                                                traj,
                                                                                restart)
        if os.path.isfile(source_path) and not is_empty_file(source_path):
            create_restarts(source_path, output_path, override=override)
        if os.path.isfile(source_path) and is_empty_file(source_path):
            copy_file(source_path, output_path, override)
