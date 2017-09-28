'''
Functions used to interface the NASQM automation routines with
the Slurm wrapper
'''
import math
import pynasqm.slurm as slurm

def create_slurm_header(user_input):
    '''
    Returns the slurm header dictionary
    '''
    return {'email': user_input.email, 'email_options': user_input.email_options,
            'n_nodes': user_input.number_nodes, 'ppn': user_input.processors_per_node,
            'memory': user_input.memory_per_node, 'walltime': user_input.walltime,
            'max_jobs': user_input.max_jobs, 'qos': user_input.qos}

def build_trajectory_command(amber, n_trajectories):
    '''
    Returns the command for the slurm script
    '''
    command = "module load intel/2016.0.109\n\n"
    command += "for i in $(seq 1 {})\n".format(n_trajectories)
    command += "do\n" \
               '    MULTIPLIER="$((${SLURM_ARRAY_TASK_ID} - 1))"\n' \
               '    FIRST_COUNT="$((${SLURM_CPUS_ON_NODE} * ${MULTIPLIER}))"\n' \
               '    ID="$((${FIRST_COUNT} + ${i}))"\n'
    command += "    $AMBERHOME/bin/sander -O -i {}${{ID}}.in -o {}".format(amber.input_roots[0],
                                                                        amber.output_roots[0])
    command += "${ID}.out -c "
    command += "{}.${{ID}} -p m1.prmtop -r ".format(amber.coordinate_files[0])
    command += "{}${{ID}}.rst -x {}".format(amber.output_roots[0], amber.output_roots[0]) \
               +"${ID}.nc &\n" \
               +"done\n" \
               +"wait\n"
    return command

def build_snapshot_command(amber, n_trajectories, amber_calls_per_trajectory):
    '''
    Returns the command for the slurm script
    '''
    command = "module load intel/2016.0.109\n\n"
    command += "for FRAME in $(seq 1 {})\n".format(amber_calls_per_trajectory)
    command += "do\n"
    command += "    for i in $(seq 1 {})\n".format(n_trajectories)
    command += "    do\n"\
               '        MULTIPLIER="$((${SLURM_ARRAY_TASK_ID} - 1))"\n' \
               '        FIRST_COUNT="$((${SLURM_CPUS_ON_NODE} * ${MULTIPLIER}))"\n' \
               '        TRAJ="$((${FIRST_COUNT} + ${i}))"\n'
    command += "        $AMBERHOME/bin/sander -O -i"
    command += " {}${{TRAJ}}.in -o {}".format(amber.input_roots[0],
                                              amber.output_roots[0])
    command += "${TRAJ}_${FRAME}.out -c "
    command += "{}${{TRAJ}}.${{FRAME}} -p m1.prmtop -r ".format(amber.coordinate_files[0])
    command += "{}${{TRAJ}}_${{FRAME}}.rst -x {}".format(amber.output_roots[0],
                                                         amber.output_roots[0]) \
               +"${TRAJ}_${FRAME}.nc &\n" \
               +"    done\n" \
               +"    wait\n" \
               +"done\n"
    return command

def build_command(amber, n_trajectories, n_snaps_per_trajectory):
    '''
    small wrapper to the build commands
    '''
    if n_snaps_per_trajectory > 1:
        return build_snapshot_command(amber, n_trajectories, n_snaps_per_trajectory)
    else:
        return build_trajectory_command(amber, n_trajectories)

def slurm_trajectory_files(user_input, amber, title, n_trajectories, amber_calls_per_trajectory):
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
        command = build_command(amber, user_input.processors_per_node, amber_calls_per_trajectory)
        slurm_script_max = slurm_script.create_slurm_script(command, title, n_arrays_max)
    if n_trajectories_remaining != 0:
        command = build_command(amber, n_trajectories_remaining, amber_calls_per_trajectory)
        slurm_script_nmax = slurm_script.create_slurm_script(command, title, 1)
    return slurm_script_max, slurm_script_nmax

def run_nasqm_slurm_files(slurm_files):
    '''
    Run the files produced by slurm_trajectory_files
    '''
    if slurm_files[0]:
        slurm.run_slurm(slurm_files[0])
    if slurm_files[1]:
        slurm.run_slurm(slurm_files[1])
