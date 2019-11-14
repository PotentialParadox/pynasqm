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

def build_trajectory_command(directory, amber):
    '''
    Returns the command for the slurm script
    '''
    inputfile = amber.input_roots[0]
    outputfile = amber.output_roots[0]
    startfile = amber.coordinate_files[0]
    restartfile = amber.restart_files[0]
    command = "source ~/myapps/load_exports\n" \
              "module load intel/2017\n" \
              "source ~/myapps/load_boost\n" \
              "source /ufrc/roitberg/dtracy/amber/amber.sh\n\n" \
              "export OMP_NUM_THREADS=${{SLURM_CPUS_PER_TASK}}\n\n" \
              "ID=${{SLURM_ARRAY_TASK_ID}}\n"\
              "cd {0}\n"\
              "$AMBERHOME/bin/sander -O -i {1}.in -o {2}.out -c {3} -p m1.prmtop -r {4} -x {2}.nc\n"\
              "cd ../../..\n".format(directory, inputfile, outputfile, startfile, restartfile)
    return command

def slurm_trajectory_files(user_input, amber, title, n_trajectories, directory):
    '''
    Run multiple sander trajectories over hpc
    '''
    slurm_header = create_slurm_header(user_input)
    slurm_script = slurm.Slurm(slurm_header)
    command = build_trajectory_command(directory, amber)
    return slurm_script.create_slurm_script(command, title, n_trajectories)

def run_nasqm_slurm_file(slurm_file):
    '''
    Run the files produced by slurm_trajectory_files
    '''
    slurm.run_slurm(slurm_file)

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
