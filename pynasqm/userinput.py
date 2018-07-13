'''
This the User Input file for the NASQM
Automation Script
'''
import json
import re
import pynasqm.utils

class UserInput:
    '''
    '''
    def __init__(self, file_name="pynasqm.in"):
        self.file_name = file_name
        data = self.get_data()
        # Change here whether your simulation is qmmm
        self.is_qmmm = pynasqm.utils.str2bool(data["is_qmmm"])
        # Change here whether you are working on your personal computer
        # or an HPC with SLUM
        self.is_hpc = pynasqm.utils.str2bool(data["is_hpc"])
        # If periodic what type of constant value are you using?
        # 1-constant volume, 2-constant pressure
        self.constant_value = int(data["constant_value"])
        # Are you performing tully surface hopping
        self.is_tully = pynasqm.utils.str2bool(data["is_tully"])
        # How many nodes will you be working on?
        self.number_nodes = int(data["number_nodes"])
        # How many processors will be on a node?
        self.processors_per_node = int(data["processors_per_node"])
        # How much memory per node
        self.memory_per_node = data["memory_per_node"]
        # What is the maximum amount of jobs you want to run at once?
        self.max_jobs = int(data["max_jobs"])
        # Prefix of the scheduler job name
        self.job_name = data["job_name"]
        # What do you want to set as your default walltime?
        self.walltime = data["walltime"]
        # Whats queue do you want the job to go to
        self.qos = data["qos"]
        # Do you want to run ground state dynamics
        self.run_ground_state_dynamics = pynasqm.utils.str2bool(data["run_ground_state_dynamics"])
        # Do you want to run the trajectories used for the abjorption specta
        self.run_absorption_trajectories = pynasqm.utils.str2bool(
            data["run_absorption_trajectories"])
        # Do you want to collect the data from the absorption calculations?
        self.run_absorption_collection = pynasqm.utils.str2bool(data["run_absorption_collection"])
        # Do you want to run the exctied state trajectories?
        self.run_excited_state_trajectories = pynasqm.utils.str2bool(
            data["run_excited_state_trajectories"])
        # Do you want to collect the data from the exctied state trajectory
        # calculations?
        self.run_fluorescence_collection = pynasqm.utils.str2bool(
            data["run_fluorescence_collection"])
        # Change here the number of snapshots you wish to take
        # from the initial ground state trajectory to run the
        # further ground state dynamics
        self.n_snapshots_gs = int(data["n_snapshots_gs"])

        # Change here the number of states you wish to
        # calculate in the absorption singlpoint calculations
        self.n_abs_exc = int(data["n_abs_exc"])

        # Change here the number of snapshots you wish to take
        # from the initial ground state trajectory to run the
        # new excited state dynamics
        self.n_snapshots_ex = int(data["n_snapshots_ex"])

        # Change here the time step that will be shared by
        # each trajectory
        self.time_step = float(data["time_step"]) # fs

        # Change here the runtime of the initial ground state MD
        self.ground_state_run_time = float(data["ground_state_run_time"]) # ps

        # Change here how often you want to print the ground state trajectory
        self.n_steps_to_print_gs = int(data["n_steps_to_print_gs"])

        # Change here the runtime for the the trajectories
        # used to create calculated the absorption
        self.abs_run_time = float(data["abs_run_time"]) # ps

        # Change here how often you want to print the absorption trajectories
        self.n_steps_to_print_abs = int(data["n_steps_to_print_abs"])

        # Change here how often you want to print to the mcrds
        try:
            self.n_steps_print_mcrd = int(data["n_steps_to_print_mcrd"])
        except KeyError:
            self.n_steps_print_mcrd = 100

        # Change here the runtime for the the trajectories
        # used to create calculated the fluorescence
        self.exc_run_time = float(data["exc_run_time"]) # ps

        # Change here the number of excited states you
        # with to have in the CIS calculation
        self.n_exc_states_propagate_ex_param = int(data["n_exc_states_propagate"])

        # Change here the initial state
        self.exc_state_init_ex_param = int(data["exc_state_init"])

        # Change here how often you want to print the excited state trajectories
        self.n_steps_to_print_exc = int(data["n_steps_to_print_exc"])

        # Some time will be needed for the molecule to equilibrate
        # from jumping from the ground state to the excited state.
        # We don't want to include this data in the calculation
        # of the fluorescence. We therefore set a time delay.
        self.fluorescence_time_delay = float(data["fluorescence_time_delay"]) # fs
        # Truncation will remove so many fs off the back of the trajectory
        self.fluorescence_time_truncation = float(data["fluorescence_time_truncation"]) # fs

        self.email = data["email"]
        # Additive Choice: 1-Begin, 2-End, 4-Fail
        self.email_options = int(data["email_options"])

        # Solvent Settings
        # This nasqm script will use cpptraj to include the nearest
        # solvent molecule in the fluorescene and absorption calculations
        # but not the initial ground state run.
        # We will default to include all solvent residues within self.nearest_radius
        # angstroms from the molecule of interest, if this is None, then
        # we will use the nearest number of solvents
        self.mask_for_center = data["mask_for_center"]
        self.number_nearest_solvents = int(data["number_nearest_solvents"])

        try:
            self.restrain_solvents = pynasqm.utils.str2bool(data["restrain_solvents"])
        except KeyError:
            self.restrain_solvents = False

        try:
            self.laser_energy = float(data['laser_energy'])
            self.fwhm = float(data['fwhm'])
        except KeyError:
            if self.run_excited_state_trajectories:
                raise KeyError('laser energy and fwhm need for excited state runs')
            else:
                pass

        ## Derived Values
        self.n_steps_gs = int(self.ground_state_run_time / self.time_step * 1000)

        self.n_mcrd_frames_gs = int(self.n_steps_gs / self.n_steps_print_mcrd)
        self.n_steps_abs = int(self.abs_run_time / self.time_step * 1000)
        # We will do absorption calculation on all
        # steps printed out, so 1 would do absorption
        # for each step during the run_abs_snapshot step
        self.n_frames_abs = int(self.n_steps_abs / self.n_steps_to_print_abs)
        self.n_mcrd_frames_abs = int(self.n_steps_abs / self.n_steps_print_mcrd)
        self.n_steps_exc = int(self.exc_run_time / self.time_step * 1000)



    def get_data(self):
        p_comment = "\s*#"
        file_stream = open(self.file_name, 'r')
        new_string = "{\n"
        for line in file_stream:
            if not re.search(p_comment, line):
                new_string += line
        new_string += "}\n"
        new_filename = "{}.json".format(self.file_name[:-3])
        open(new_filename, 'w').write(new_string)
        with open(new_filename, 'r') as data_file:
            return json.load(data_file)

