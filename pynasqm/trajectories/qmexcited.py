class QmExcited:

    def __init__(self, user_input, input_ceon):
        self.user_input = user_input
        self.input_ceons = [input_ceon]
        self.number_trajectories = user_input.n_snapshots_ex
        self.child_root = 'nasqm_qmexcited_'
        self.job_suffix = 'qmexcited'
        self.parent_restart_root = 'nasqm_qmground_'
        self.amber_restart = True
