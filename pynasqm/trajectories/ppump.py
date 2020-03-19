class PPump:

    def __init__(self, user_input, input_ceon):
        self.user_input = user_input
        self.input_ceons = [input_ceon]
        self.number_trajectories = user_input.n_snapshots_ex
        self.child_root = 'nasqm_pulse_pump_'
        self.job_suffix = 'pulse_pump'
        self.parent_restart_root = 'nasqm_qmground_'
        self.amber_restart = True

    def __str__(self):
        print_value = ""\
            f"Traj_Data Info:\n"\
            f"Class: {self.job_suffix}:\n"\
            f"Number input_ceons: {len(self.input_ceons)}\n"\
            f"Number trajectories: {self.number_trajectories}\n"
        return print_value
