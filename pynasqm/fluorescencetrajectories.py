from pynasqm.trajectories import Trajectories
import pynasqm.cpptraj as nasqm_cpptraj

class FluTrajectories(Trajectories):

    def __init__(self, user_input, input_ceon):
        self._user_input = user_input
        self._input_ceons = [input_ceon]
        self._number_trajectories = user_input.n_snapshots_ex
        self._child_root = 'nasqm_flu_'
        self._job_suffix = '_f_'
        self._parent_restart_root = 'nasqm_abs_'
        self._amber_restart = True

    def _restart_name(self, index):
        if index == -1:
            return "{}{}.rst".format(self._parent_restart_root, 1)
        return "{}{}.rst".format(self._parent_restart_root, index+1)

    def _trajins(self):
        trajins = []
        for i in range(1, self._number_trajectories +1):
            trajins.append("{}{}.rst".format(self._parent_restart_root, i))
        return trajins
