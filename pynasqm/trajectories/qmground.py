class QmGround:

    def __init__(self, user_input, input_ceon):
        self.user_input = user_input
        self.input_ceons = [input_ceon]
        self.number_trajectories = user_input.n_snapshots_qmground
        self.child_root = 'nasqm_qmground_'
        self.job_suffix = 'qmground'
        self.parent_restart_root = 'ground_snap'
        self.number_frames_in_parent = user_input.n_mcrd_frames_per_run_gs * user_input.n_ground_runs
        self.amber_restart = False

    def __str__(self):
        print_value = ""\
            f"Traj_Data Info:\n"\
            f"Class: {self.job_suffix}:\n"\
            f"Number input_ceons: {len(self.input_ceons)}\n"\
            f"Number trajectories: {self.number_trajectories}\n"
        return print_value
