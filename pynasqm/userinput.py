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
        #################################
        # Slurm Specific
        #################################
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
        # If doing surface hoping, how many quantum steps per each classical [4]
        try:
            self.qsteps = int(data["qsteps"])
        except KeyError:
            self.qsteps = 4
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
        # Email
        self.email = data["email"]
        # Additive Choice: 1-Begin, 2-End, 4-Fail
        self.email_options = int(data["email_options"])


        #################################
        # Global Trajectory
        #################################
        # Change here the time step that will be shared by
        # each trajectory
        self.time_step = float(data["time_step"]) # fs

        #################################
        # MM Ground State
        #################################
        # Do you want to run ground state dynamics
        self.run_ground_state_dynamics = pynasqm.utils.str2bool(data["run_ground_state_dynamics"])
        # Change here the number of restarts of length ground_state_run_time you wish to run
        try:
            self.n_ground_runs = int(data["n_ground_runs"])
        except KeyError:
            self.n_ground_runs = 1
        # Change here how often you want to print to the groundstae mcrds
        try:
            self.n_steps_print_gmcrd = int(data["n_steps_to_print_gmcrd"])
        except KeyError:
            self.n_steps_print_gmcrd = 100
        # Change here how often you want to print the ground state trajectory
        self.n_steps_to_print_gs = int(data["n_steps_to_print_gs"])
        # Change here the number of snapshots you wish to take
        # from the initial ground state trajectory to run the
        # further ground state dynamics
        self.n_snapshots_gs = int(data["n_snapshots_gs"])
        # Change here the runtime of the initial ground state MD
        self.ground_state_run_time = float(data["ground_state_run_time"]) # ps
        self.ground_state_run_time = self.adjust_run_time(self.ground_state_run_time,
                                                          self.time_step,
                                                          self.n_ground_runs,
                                                          self.n_steps_print_gmcrd,
                                                          self.n_snapshots_gs)

        #################################
        # QM Ground State
        #################################
        # Do you want to run the trajectories used for the abjorption specta
        self.run_absorption_trajectories = pynasqm.utils.str2bool(
            data["run_absorption_trajectories"])
        # Change here the number of restarts of length abs_run_time you wish to run
        try:
            self.n_abs_runs = int(data["n_abs_runs"])
        except KeyError:
            self.n_abs_runs = 1
        # Change here the number of states you wish to
        # calculate in the absorption singlpoint calculations
        self.n_abs_exc = int(data["n_abs_exc"])
        # Change here how often you want to print the absorption trajectories
        self.n_steps_to_print_abs = int(data["n_steps_to_print_abs"])
        try:
            self.n_steps_print_amcrd = int(data["n_steps_to_print_amcrd"])
        except KeyError:
            self.n_steps_print_amcrd = 0
        # Do you want to collect the data from the absorption calculations?
        self.run_absorption_collection = pynasqm.utils.str2bool(data["run_absorption_collection"])
        # Some time will be needed for the molecule to equilibrate
        # from jumping from MM to QM.
        # We don't want to include this data in the calculation
        # of the fluorescence. We therefore set a time delay.
        try:
            self.abs_time_delay = float(data["absorption_time_delay"]) # fs
        except KeyError:
            print("Absorption time delay wasn't given defaulting to 1ps")
            self.abs_time_delay = 1000
        # Change here the runtime for the the trajectories
        # used to create calculated the absorption
        # Number of snapshots is negligible for adjustment because exc will use final snapshot
        # and is set to 1, if abs runtime is not equal 0 we want to make it reasonable to work with the other inputs
        self.abs_run_time = float(data["abs_run_time"]) # ps
        if self.abs_run_time != 0 and self.n_steps_print_amcrd != 0:
            self.abs_run_time = self.adjust_run_time(self.abs_run_time,
                                                     self.time_step,
                                                     self.n_abs_runs,
                                                     self.n_steps_print_amcrd,
                                                     1)

        #################################
        # QM Excited State
        #################################
        # Do you want to run the exctied state trajectories?
        self.run_excited_state_trajectories = pynasqm.utils.str2bool(
            data["run_excited_state_trajectories"])
        # Change here the number of restarts of length exc_run_time you wish to run
        try:
            self.n_exc_runs = int(data["n_exc_runs"])
        except KeyError:
            self.n_exc_runs = 1
        # Change here the number of snapshots you wish to take
        # from the initial ground state trajectory to run the
        # new excited state dynamics
        self.n_snapshots_ex = int(data["n_snapshots_ex"])
        if self.n_snapshots_ex > self.n_snapshots_gs:
            raise ValueError("\nCurrently esmd runs start from the restarts of qmmm_gsmd\n"\
                             "therefore n_snapshots_ex must less than or equal to n_snapshots_gs")
        # Do you want to collect the data from the exctied state trajectory
        # calculations?
        self.run_fluorescence_collection = pynasqm.utils.str2bool(
            data["run_fluorescence_collection"])
        # Change here how often you want to print the fluorescence trajectories
        try:
            self.n_steps_print_emcrd = int(data["n_steps_to_print_emcrd"])
        except KeyError:
            self.n_steps_print_emcrd = 0
        # Change here the number of excited states you
        # with to have in the CIS calculation
        self.n_exc_states_propagate_ex_param = int(data["n_exc_states_propagate"])
        # Change here the initial state
        try:
            self.exc_state_init_ex_param = int(data["exc_state_init"])
        except KeyError:
            raise KeyError(
                'excited_state init param not set, please use either -2 for pump-pulse, -1 for'\
                'laser, or manually set initial state')
        if self.exc_state_init_ex_param == -1:
            try:
                self.laser_energy = float(data['laser_energy'])
                self.fwhm = float(data['fwhm'])
            except KeyError:
                if self.run_excited_state_trajectories:
                    raise KeyError('laser energy and fwhm needed for excited state runs')
                else:
                    pass
        if self.exc_state_init_ex_param == -2:
            self.is_pulse_pump = True
        # Change here how often you want to print the excited state trajectories
        self.n_steps_to_print_exc = int(data["n_steps_to_print_exc"])
        # Some time will be needed for the molecule to equilibrate
        # from jumping from the ground state to the excited state.
        # We don't want to include this data in the calculation
        # of the fluorescence. We therefore set a time delay.
        self.fluorescence_time_delay = float(data["fluorescence_time_delay"]) # fs
        # Truncation will remove so many fs off the back of the trajectory
        self.fluorescence_time_truncation = float(data["fluorescence_time_truncation"]) # fs
        # Change here the runtime for the the trajectories
        # used to create calculated the fluorescence
        self.exc_run_time = float(data["exc_run_time"]) # ps
        if self.n_steps_print_emcrd != 0:
            self.exc_run_time = self.adjust_run_time(self.exc_run_time,
                                                    self.time_step,
                                                    self.n_exc_runs,
                                                    self.n_steps_print_emcrd,
                                                    1)


        #################################
        # Solvent Settings
        #################################
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


        #################################
        # Derived Values
        #################################
        self.restart_attempt = 0
        self.n_steps_gs = self.n_steps(self.ground_state_run_time, self.time_step,
                                       self.n_ground_runs)
        self.n_mcrd_frames_gs = int(self.n_steps_gs / self.n_steps_print_gmcrd)
        self.n_steps_abs = self.n_steps(self.abs_run_time, self.time_step, self.n_abs_runs)
        self.n_frames_abs = int(self.n_steps_abs / self.n_steps_to_print_abs)
        self.n_steps_exc = self.n_steps(self.exc_run_time, self.time_step, self.n_exc_runs)


    @staticmethod
    def n_steps(run_time, time_step, n_runs):
        return int(run_time / (time_step * n_runs) * 1000)

    def adjust_run_time(self, run_time, time_step, n_runs, n_print_trajs, n_trajs):
        total_frames = self.time_to_frame(run_time, time_step, n_print_trajs)
        divisor = pynasqm.utils.lcmoflist([n_trajs, n_runs])
        new_frames = self.make_divisible(total_frames, divisor)
        new_time = self.frames_to_time(new_frames, time_step, n_print_trajs)
        if new_time / total_frames > 1.1:
            raise ValueError("Input values would require an adjustment to given time by more than 1.1.\n"\
                             "Please adjust you inputs to allow an even distribution of time among restarts")
        if new_time != run_time:
            print("Had to adjust runtime to allow for even distribution\n"\
                  "Time changed from {} to {}".format(run_time, new_time))
        return new_time

    @staticmethod
    def make_divisible(val, cons):
        if val % cons == 0:
            return val
        newval = val + (cons - (val % cons))
        if newval % cons != 0:
            raise AssertionError("Failed to make {} divisible by {}".format(val, cons))
        return newval

    def time_to_frame(self, run_time, time_step, n_print_trajs):
        return run_time / ((time_step/1000) * n_print_trajs)

    def frames_to_time(self, n_frames, time_step, n_print_trajs):
        new_time = n_frames * (time_step/1000) * n_print_trajs
        return new_time

    def get_data(self):
        p_comment = r"\s*#"
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

