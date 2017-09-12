'''
This the User Input file for the NASQM
Automation Script
'''
class UserInput:
    '''
    Contains the data for the users to change at will
    '''
    def __init__(self):
        # Change here whether your simulation is qmmm
        self.is_qmmm = True
        # Change here whether you are working on your personal computer
        # or an HPC with SLUM
        self.is_hpc = False
        # Are you performing tully surface hopping
        self.is_tully = False
        # How many nodes will you be working on?
        self.number_nodes = 1
        # How many processors will be on a node?
        self.processors_per_node = 4
        # How much memory per node
        self.memory_per_node = "2000mb"
        # What is the maximum amount of jobs you want to run at once?
        self.max_jobs = 4
        # What do you want to set as your default walltime?
        self.walltime = "01:00:00"
        # Whats queue do you want the job to go to
        self.qos = "roitberg-b"
        # Do you want to run ground state dynamics
        self.run_ground_state_dynamics = True
        # Do you want to run the trajectories used for the abjorption specta
        self.run_absorption_trajectories = False
        # Do you want to run the single point snapshots from these
        # absorption
        self.run_absorption_snapshots = False
        # Do you want to collect the data from the absorption calculations?
        self.run_absorption_collection = False
        # Do you want to run the exctied state trajectories?
        self.run_excited_state_trajectories = False
        # Do you want to collect the data from the exctied state trajectory
        # calculations?
        self.run_fluorescence_collection = False

        # Change here the number of snapshots you wish to take
        # from the initial ground state trajectory to run the
        # further ground state dynamics
        self.n_snapshots_gs = 1

        # Change here the number of states you wish to
        # calculate in the absorption singlpoint calculations
        self.n_abs_exc = 5

        # Change here the number of snapshots you wish to take
        # from the initial ground state trajectory to run the
        # new excited state dynamics
        self.n_snapshots_ex = 1

        # Change here the time step that will be shared by
        # each trajectory
        self.time_step = 0.5  # fs

        # Change here the runtime of the initial ground state MD
        self.ground_state_run_time = 10 # ps

        # Change here how often you want to print the ground state trajectory
        self.n_steps_to_print_gs = 50

        # Change here the runtime for the the trajectories
        # used to create calculated the absorption
        self.abs_run_time = 5 # ps

        # Change here how often you want to print the absorption trajectories
        self.n_steps_to_print_abs = 50

        # Change here the runtime for the the trajectories
        # used to create calculated the fluorescence
        self.exc_run_time = 5 # ps

        # Change here the number of excited states you
        # with to have in the CIS calculation
        self.n_exc_states_propagate_ex_param = 1

        # Change here the initial state
        self.exc_state_init_ex_param = 1

        # Change here how often you want to print the excited state trajectories
        self.n_steps_to_print_exc = 50

        # Some time will be needed for the molecule to equilibrate
        # from jumping from the ground state to the excited state.
        # We don't want to include this data in the calculation
        # of the fluorescence. We therefore set a time delay.
        self.fluorescence_time_delay = 2 # fs
        # Truncation will remove so many fs off the back of the trajectory
        self.fluorescence_time_truncation = 0 # fs

        # Solvent Settings
        # This nasqm script will use cpptraj to include the nearest
        # solvent molecule in the fluorescene and absorption calculations
        # but not the initial ground state run.
        # We will default to include all solvent residues within self.nearest_radius
        # angstroms from the molecule of interest, if this is None, then
        # we will use the nearest number of solvents
        self.number_nearest_solvents = None

        ## Derived Values
        self.n_steps_gs = int(self.ground_state_run_time / self.time_step * 1000)
        self.n_frames_gs = int(self.n_steps_gs / self.n_steps_to_print_gs)
        self.n_steps_abs = int(self.abs_run_time / self.time_step * 1000)
        # We will do absorption calculation on all
        # steps printed out, so 1 would do absorption
        # for each step during the run_abs_snapshot step
        self.n_frames_abs = int(self.n_steps_abs / self.n_steps_to_print_abs)
        self.n_steps_exc = int(self.exc_run_time / self.time_step * 1000)

        self.email = "dtracy.uf@gmail.com"
        # Additive Choice: 1-Begin, 2-End, 4-Fail
        self.email_options = 3
