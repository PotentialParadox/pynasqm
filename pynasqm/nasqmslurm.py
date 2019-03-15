'''
Functions used to interface the NASQM automation routines with
the Slurm wrapper
'''
import math
import os
import pynasqm.slurm as slurm

def create_slurm_header(user_input):
    '''
    Returns the slurm header dictionary
    '''
    return {'email': user_input.email, 'email_options': user_input.email_options,
            'n_nodes': user_input.number_nodes, 'ppn': user_input.processors_per_node,
            'memory': user_input.memory_per_node, 'walltime': user_input.walltime,
            'max_jobs': user_input.max_jobs, 'qos': user_input.qos}

def build_trajectory_command(directory, amber, n_trajectories, start):
    '''
    Returns the command for the slurm script
    '''
    inputfile = amber.input_roots[0]
    outputfile = amber.output_roots[0]
    startfile = amber.coordinate_files[0]
    restartfile = amber.restart_files[0]
    command = "module load intel/2017\n\n"
    command += "for i in $(seq {} {})\n".format(start, start+n_trajectories-1)
    command += "do\n" \
               '    MULTIPLIER="$((${SLURM_ARRAY_TASK_ID} - 1))"\n' \
               '    FIRST_COUNT="$((${SLURM_CPUS_ON_NODE} * ${MULTIPLIER}))"\n' \
               '    ID="$((${FIRST_COUNT} + ${i}))"\n'
    command += "    cd {}\n".format(directory)
    command += "    $AMBERHOME/bin/sander -O -i {}.in -o {}.out ".format(inputfile,
                                                                    outputfile)
    command += "-c {} -p m1.prmtop ".format(startfile)
    command += "-r {} -x {}.nc &\n".format(restartfile, outputfile) \
               + "    cd ../../..\n" \
               "done\n" \
               "wait\n"
    return command

def slurm_trajectory_files(user_input, amber, title, n_trajectories, directory):
    '''
    Run multiple sander trajectories over hpc
    '''
    n_arrays_max = math.floor(n_trajectories/user_input.processors_per_node)
    n_trajectories_remaining = n_trajectories - n_arrays_max * user_input.processors_per_node
    slurm_header = create_slurm_header(user_input)
    slurm_script = slurm.Slurm(slurm_header)
    slurm_script_max = None
    slurm_script_nmax = None
    if n_arrays_max != 0:
        command = build_trajectory_command(directory, amber, user_input.processors_per_node, 1)
        slurm_script_max = slurm_script.create_slurm_script(command, title, n_arrays_max)
    if n_trajectories_remaining != 0:
        start_trajectory = n_arrays_max*user_input.processors_per_node+1
        command = build_trajectory_command(directory, amber, n_trajectories_remaining, start_trajectory)
        slurm_script_nmax = slurm_script.create_slurm_script(command, title, 1)
    return slurm_script_max, slurm_script_nmax

def run_nasqm_slurm_files(slurm_files):
    '''
    Run the files produced by slurm_trajectory_files
    '''
    slurm.run_slurm(slurm_files[0], slurm_files[1])

def create_restart_header(user_input):
    header = create_slurm_header(user_input)
    header["walltime"] = "95:00:00"
    header["ppn"] = 1
    return header

def build_restart_command(job_id, restart_attempt):
    return "source ~/myapps/load_exports\n"\
        "module load intel/2017\n"\
        "source /ufrc/roitberg/dtracy/amber/amber.sh\n"\
        "\n"\
        "nasqm.py --job {} --restart {}".format(job_id, restart_attempt)

def nasqm_restart_script(user_input, job_id, restart_attempt):
    header = create_restart_header(user_input)
    restart_command = build_restart_command(job_id, restart_attempt)
    title = "{}_r{}".format(user_input.job_name.capitalize(), restart_attempt)
    max_arrays = 1
    slurm_script = slurm.Slurm(header)
    return slurm_script.create_slurm_script(restart_command, title, max_arrays)

def restart_nasqm(user_input, job_id, restart_attempt):
    script = nasqm_restart_script(user_input, job_id, restart_attempt)
    script_filename = "pynasqm_restart.sbatch"
    slurm.submit_job(script_filename, script)
    exit()
