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
        try:
            self.time_step = float(data["time_step"]) # fs
        except KeyError:
            self.time_step = 0

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
        # Change here the number of further qm ground state trajectories
        self.n_snapshots_qmground = int(data["n_snapshots_qmground"])
        # Change here the runtime of the initial ground state MD
        try:
            self.ground_state_time_step = float(data["ground_state_time_step"]) # fs
        except KeyError:
            self.ground_state_time_step = self.time_step
        self.ground_state_run_time = float(data["ground_state_run_time"]) # ps
        self.ground_state_run_time = self.adjust_run_time(self.ground_state_run_time,
                                                          self.ground_state_time_step,
                                                          self.n_ground_runs,
                                                          self.n_steps_print_gmcrd,
                                                          self.n_snapshots_qmground)

        #################################
        # QM Ground State
        #################################
        # Do you want to run the trajectories used for the abjorption specta
        self.run_qmground_trajectories = pynasqm.utils.str2bool(
            data["run_qmground_trajectories"])
        # A file containing the indices of the trajectories you wish to run
        try:
            self.qmground_traj_index_file = data["qmground_traj_index_file"]
        except KeyError:
            self.qmground_traj_index_file = ""
        # Change here the number of restarts of length qmground_run_time you wish to run
        try:
            self.n_qmground_runs = int(data["n_qmground_runs"])
        except KeyError:
            self.n_qmground_runs = 1
        # Change here the number of states you wish to
        # calculate in the qmgroundorption singlpoint calculations
        self.n_qmground_exc = int(data["n_qmground_exc"])
        # Change here how often you want to print the qmgroundorption trajectories
        self.n_steps_to_print_qmground = int(data["n_steps_to_print_qmground"])
        try:
            self.n_steps_print_qmgmcrd = int(data["n_steps_to_print_qmgmcrd"])
        except KeyError:
            self.n_steps_print_qmgmcrd = 0
        # Change here the runtime for the qmground trajectories
        self.qmground_run_time = float(data["qmground_run_time"]) # ps
        try:
            self.qmground_time_step = float(data["qmground_time_step"]) # fs
        except KeyError:
            self.qmground_time_step = self.time_step

        if self.qmground_run_time != 0 and self.n_steps_print_qmgmcrd != 0:
            self.qmground_run_time = self.adjust_run_time(self.qmground_run_time,
                                                     self.qmground_time_step,
                                                     self.n_qmground_runs,
                                                     self.n_steps_print_qmgmcrd,
                                                     1)

        #################################
        # Absorption Snapshots
        #################################
        # Do you want to run the absorption snapshots
        self.run_absorption_snapshots = pynasqm.utils.str2bool(data["run_absorption_snapshots"])
        self.n_abs_exc = int(data["n_abs_exc"])
        # Some time will be needed for the molecule to equilibrate
        # from jumping from MM to QM.
        # We don't want to include this data in the calculation
        # of the absorption. We therefore set a time delay.
        try:
            self.absorption_time_delay = float(data["absorption_time_delay"]) # fs
        except KeyError:
            print("Absorption time delay wasn't given defaulting to 0 fs")
            self.absorption_time_delay = 0
        # Do you want to collect the data from the qmgroundorption calculations?
        self.run_absorption_collection = pynasqm.utils.str2bool(data["run_absorption_collection"])

        #################################
        # Pulse Pump Snapshots
        #################################
        # Are you performing pulse pump simulation?
        try:
            self.run_pulse_pump_singlepoints = pynasqm.utils.str2bool(
                data["run_pulse_point_singlepoints"])
            self.pump_pulse_min_energy = float(data["pump_pulse_min_energy"])
            self.pump_pulse_max_energy = float(data["pump_pulse_max_energy"])
            self.pump_pulse_min_strength = float(data["pump_pulse_min_strength"])
            # Change here the number of excited states you
            # with to have in the CIS calculation
            try:
                self.n_pulsepump_excited_states = int(data["n_pulsepump_excited_states"])
            except KeyError:
                self.n_pulsepump_excited_states = int(data["n_exc_states_propagate"])
            try:
                self.run_pulse_pump_collection = pynasqm.utils.str2bool(
                    data["run_pulse_point_collection"])
            except KeyError:
                if self.run_pulse_pump_singlepoints:
                    self.run_pulse_pump_collection = True
        except KeyError:
            self.run_pulse_pump_singlepoints = False
            self.run_pulse_pump_collection= False


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
        # A file containing the indices of the trajectories you wish to run
        try:
            self.qmexcited_traj_index_file = data["qmexcited_traj_index_file"]
        except KeyError:
            self.qmexcited_traj_index_file = ""

        if self.n_snapshots_ex > self.n_snapshots_qmground:
            raise ValueError("\nCurrently esmd runs start from the restarts of qmmm_gsmd\n"\
                             "therefore n_snapshots_ex must less than or equal to n_snapshots_qmground")
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
        else:
            self.is_pulse_pump = False
        # Change here how often you want to print the excited state trajectories
        self.n_steps_to_print_exc = int(data["n_steps_to_print_exc"])
        # Change here the runtime for the the trajectories
        # used to create calculated the fluorescence
        self.exc_run_time = float(data["exc_run_time"]) # ps
        try:
            self.exc_time_step = float(data["exc_time_step"]) # fs
        except KeyError:
            self.exc_time_step = self.time_step

        if self.n_steps_print_emcrd != 0:
            self.exc_run_time = self.adjust_run_time(self.exc_run_time,
                                                    self.exc_time_step,
                                                    self.n_exc_runs,
                                                    self.n_steps_print_emcrd,
                                                    1)
        #################################
        # Fluorescence
        #################################
        # Do you want to run the fluorescence snapshots
        try:
            self.run_fluorescence_snapshots = pynasqm.utils.str2bool(data["run_fluorescence_snapshots"])
        except KeyError:
            self.run_fluorescence_snapshots = False
        # Number of states to include in the fluorescence calculations
        try:
            self.n_flu_exc = int(data["n_flu_exc"])
        except KeyError:
            self.n_flu_exc = 1
        # Some time will be needed for the molecule to equilibrate
        # from jumping from the ground state to the excited state.
        # We don't want to include this data in the calculation
        # of the fluorescence. We therefore set a time delay.
        self.fluorescence_time_delay = float(data["fluorescence_time_delay"]) # fs
        # Truncation will remove so many fs off the back of the trajectory
        self.fluorescence_time_truncation = float(data["fluorescence_time_truncation"]) # fs
        # Do you want to collect the data from the exctied state trajectory
        # calculations?
        self.run_fluorescence_collection = pynasqm.utils.str2bool(
            data["run_fluorescence_collection"])


        #################################
        # Solvent Settings
        #################################
        # This nasqm script will use cpptraj to include the nearest
        # solvent molecule in the fluorescene and qmgroundorption calculations
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
        self.n_steps_per_run_gs = self.n_steps_per_run(self.ground_state_run_time, self.ground_state_time_step,
                                       self.n_ground_runs)
        self.n_mcrd_frames_per_run_gs = int(self.n_steps_per_run_gs / self.n_steps_print_gmcrd)
        self.n_steps_per_run_qmground = self.n_steps_per_run(self.qmground_run_time, self.qmground_time_step, self.n_qmground_runs)
        self.n_frames_per_run_qmground = int(self.n_steps_per_run_qmground / self.n_steps_to_print_qmground)
        self.n_mcrd_frames_per_run_qmground = int(self.n_steps_per_run_qmground / self.n_steps_print_qmgmcrd)
        self.n_steps_per_run_exc = self.n_steps_per_run(self.exc_run_time, self.exc_time_step, self.n_exc_runs)
        self.n_mcrd_frames_per_run_qmexcited = int(self.n_steps_per_run_exc / self.n_steps_print_emcrd)


    @staticmethod
    def n_steps_per_run(run_time, time_step, n_runs):
        return int(run_time / (time_step * n_runs) * 1000)

    def adjust_run_time(self, run_time, time_step, n_runs, n_print_trajs, n_trajs):
        total_frames = self.time_to_frame(run_time, time_step, n_print_trajs)
        divisor = pynasqm.utils.lcmoflist([n_trajs, n_runs])
        new_frames = self.make_divisible(total_frames, divisor)
        new_time = self.frames_to_time(new_frames, time_step, n_print_trajs)
        if new_time / total_frames > 1.1:
            raise ValueError(f"Input values would require an adjustment to given time by more than 1.1.\n"\
                             f"run_time = {run_time}\n"\
                             f"time_step = {time_step}\n"\
                             f"n_runs = {n_runs}\n"\
                             f"n_print_trajs = {n_print_trajs}\n"\
                             f"n_trajs = {n_trajs}\n"\
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

