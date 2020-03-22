class Absorption:

    def __init__(self, user_input, input_ceon):
        self.user_input = user_input
        self.input_ceons = [input_ceon]
        self.number_trajectories = user_input.n_snapshots_qmground
        self.child_root = 'nasqm_absorption_'
        self.job_suffix = 'absorption'
        self.parent_restart_root = 'nasqm_qmground'
        self.number_frames_in_parent = user_input.n_mcrd_frames_per_run_qmground * user_input.n_qmground_runs
        self.n_snapshots_per_trajectory = self.snaps_per_trajectory()
        self.amber_restart = False

    def __str__(self):
        print_value = ""\
            f"Traj_Data Info: \n"\
            f"Class: Absorption\n"\
            f"Number input_ceons: {len(self.input_ceons)}\n"\
            f"Number trajectories: {self.number_trajectories}\n"
        return print_value

    def snaps_per_trajectory(self):
        n_frames = self.number_frames_in_parent
        run_time = self.user_input.qmground_run_time
        time_delay = self.user_input.absorption_time_delay/1000
        return int(n_frames * ( 1 - time_delay/run_time))
