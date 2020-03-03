pynasqmin = ''\
'# -*- Mode: json -*-\n'\
'############################################################\n'\
'#                  HPC Info (Slurm Supported)\n'\
'############################################################\n'\
'# Change here whether you are working on your personal computer\n'\
'# or an HPC with SLURM\n'\
'    "is_hpc": "False",\n'\
'# If on hpc, what is the name of your job?\n'\
'    "job_name": "vac",\n'\
'# How many nodes will you be working on?\n'\
'    "number_nodes": "1",\n'\
'# How many processors will be on a node?\n'\
'    "processors_per_node": "16",\n'\
'# How much memory per node, provide string\n'\
'    "memory_per_node": "2000mb",\n'\
'# What is the maximum amount of jobs you want to run at once?\n'\
'    "max_jobs": "4",\n'\
'# What do you want to set as your default walltime?\n'\
'# 0h:0m:0s\n'\
'    "walltime": "95:00:00",\n'\
'# Whats queue do you want the job to go to\n'\
'    "qos": "roitberg-b",\n'\
'# These are your email options for the slurm interface\n'\
'    "email": "dtracy.uf@gmail.com",\n'\
'# Additive Choice: 1-Begin, 2-End, 4-Fail\n'\
'    "email_options": "3",\n'\
'############################################################\n'\
'#                  General Job Type\n'\
'############################################################\n'\
'# Change here whether your simulation is qmmm\n'\
'    "is_qmmm": "True",\n'\
'# If periodic what type of constant value are you using?\n'\
'# 1-constant volume, 2-constant pressure\n'\
'    "constant_value": "1",\n'\
'# Are you performing tully surface hopping?\n'\
'    "is_tully": "False",\n'\
'# If you are using tully, how many quantum steps should be performed for every classical?\n'\
'    "qsteps": "4",\n'\
'# Change here the time step, in fs, that will be shared by\n'\
'# each trajectory\n'\
'    "time_step": "0.5",\n'\
'############################################################\n'\
'#                  MM Ground State Calculation\n'\
'############################################################\n'\
'# Do you want to run ground state dynamics\n'\
'    "run_ground_state_dynamics": "False",\n'\
'# Change here the runtime, in ps, of the initial ground state MD\n'\
'    "ground_state_run_time": "0.01",\n'\
'# Change here the number of restarts of length ground_state_run_time you wish to run\n'\
'    "n_ground_runs": "2",\n'\
'# Change here how often you want to print the ground state trajectory files\n'\
'    "n_steps_to_print_gmcrd": "5",\n'\
'# Change here how often you want to print the ground state trajectory\n'\
'    "n_steps_to_print_gs": "5",\n'\
'############################################################\n'\
'#                  QM Ground State Calculation\n'\
'############################################################\n'\
'# Do you want to run the trajectories used for the abjorption specta\n'\
'    "run_qmground_trajectories": "False",\n'\
'# Change here the number of snapshots you wish to take\n'\
'# from the initial ground state trajectory to run the\n'\
'# further ground state dynamics\n'\
'    "n_snapshots_qmground": "2",\n'\
'# File listing the trajectories you wish to run\n'\
'# Leave black to run all\n'\
'    "qmground_traj_index_file": "",\n'\
'# Change here the runtime in PS for the the trajectories\n'\
'# used to create calculated the absorption\n'\
'    "qmground_run_time": "0.004",\n'\
'# Number of restarts = this number - 1. Controls how you want to segmentate\n'\
'# the runs for shorter run times, and to allow restarting if failure arises\n'\
'    "n_qmground_runs": "1",\n'\
'# Change here how often you want to print the absorption trajectory files\n'\
'# Use -1 to skip\n'\
'    "n_steps_to_print_qmgmcrd": "5",\n'\
'# Change here how often you want to print the absorption trajectories\n'\
'    "n_steps_to_print_qmground": "4",\n'\
'# Change here the number of states you wish to\n'\
'# calculate in the absorption singlpoint calculations\n'\
'    "n_qmground_exc": "5",\n'\
'############################################################\n'\
'#                  Absorption\n'\
'############################################################\n'\
'# Do you want to run the single point snapshots from these\n'\
'# absorption\n'\
'    "run_absorption_snapshots": "False",\n'\
'# How many excited states do you want to include in the absorption\n'\
'# calculation\n'\
'    "n_abs_exc": "10",\n'\
'# Do you want to collect the data from the absorption calculations?\n'\
'    "run_absorption_collection": "False",\n'\
'# Some time will be needed for the molecule to equilibrate\n'\
'# from jumping from the MM to QM\n'\
'# We don\'t want to include this data in the calculation\n'\
'# We therefore set a time delay in fs.\n'\
'    "absorption_time_delay": "000",\n'\
'############################################################\n'\
'#                  Pump Pulse Simulation\n'\
'############################################################\n'\
'# Do you want to run the pulse pump singlepoins?\n'\
'    "run_pulse_point_singlepoints": "False",\n'\
'# Whats the minimum energy of the pump pulse state Sm?\n'\
'    "pump_pulse_min_energy": "0",\n'\
'# Whats the maximum energy of the pump pulse state Sm?\n'\
'    "pump_pulse_max_energy": "0",\n'\
'# Whats the minimum oscillator strength from S1 of the pump pulse state Sm?\n'\
'    "pump_pulse_min_strength": "0",\n'\
'# Do you want to run the pulse pump collection routine?\n'\
'    "run_pulse_point_collection": "False",\n'\
'############################################################\n'\
'#                  Excited State Calculation\n'\
'############################################################\n'\
'# Do you want to run the exctied state trajectories?\n'\
'    "run_excited_state_trajectories": "False",\n'\
'# Change here the number of snapshots you wish to take\n'\
'# from the initial ground state trajectory to run the\n'\
'# new excited state dynamics. Needs to be <= n_snapshots_gs\n'\
'    "n_snapshots_ex": "2",\n'\
'# File listing the trajectories you wish to run\n'\
'# Leave black to run all\n'\
'    "qmexcited_traj_index_file": "",\n'\
'# Change here the runtime, in ps, for the the trajectories\n'\
'# used to create calculated the fluorescence\n'\
'    "exc_run_time": "0.002",\n'\
'# Number of restarts = this number - 1. Controls how you want to segmentate\n'\
'# the runs for shorter run times, and to allow restarting if failure arises\n'\
'    "n_exc_runs": "2",\n'\
'# Change here how often you want to print the excited state trajectory files\n'\
'# Use -1 to skip\n'\
'    "n_steps_to_print_emcrd": "5",\n'\
'# Change here how often you want to print the excited state trajectories\n'\
'    "n_steps_to_print_exc": "10",\n'\
'# Change here the number of excited states you\n'\
'# with to have in the CIS calculation\n'\
'    "n_exc_states_propagate": "5",\n'\
'# Change here the initial state, set to "-1" if you want to simulate laser exitation.\n'\
'# Change to -2 for pump pulse simulation\n'\
'    "exc_state_init": "1",\n'\
'# Change here the energy of the laser used for excitation?\n'\
'    "laser_energy": "4.2",\n'\
'# Change here the full width half max of the laser in fs\n'\
'# Note that 100fs FWHM of a laser will correspond to a 0.162eV FWHM FC broadening\n'\
'    "fwhm": "100",\n'\
'# Do you want to collect the data from the exctied state trajectory\n'\
'# calculations?\n'\
'    "run_fluorescence_collection": "False",\n'\
'# Some time will be needed for the molecule to equilibrate\n'\
'# from jumping from the ground state to the excited state.\n'\
'# We don\'t want to include this data in the calculation\n'\
'# of the fluorescence. We therefore set a time delay in fs.\n'\
'    "fluorescence_time_delay": "0000",\n'\
'# Truncation will remove so many fs off the back of the trajectory\n'\
'    "fluorescence_time_truncation": "0000",\n'\
'############################################################\n'\
'#                  QM Solvents\n'\
'############################################################\n'\
'# Do you want to restrain the closest solvents?\n'\
'    "restrain_solvents": "False",\n'\
'# The amber mask to determine the center of your system\n'\
'    "mask_for_center": ":1",\n'\
'# Number of solvents closest to mask to include in qm\n'\
'    "number_nearest_solvents": "0"\n'\
'\n'
