from pynasqm.trajectories import Trajectories
import pynasqm.cpptraj as nasqm_cpptraj
from pynasqm.initialexcitedstates import get_n_initial_states_w_laser_energy_and_fwhm

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

    def _create_inputceon_copies(self):
        input_ceons = []
        for index in range(1, self._number_trajectories+1):
            file_name = "{}{}.in".format(self._child_root, index)
            input_ceons.append(self._input_ceons[0].copy("{}/".format(index), file_name))
        init_states = get_n_initial_states_w_laser_energy_and_fwhm(self._number_trajectories,
                                                                   'spectra_abs.input',
                                                                   self._user_input.laser_energy,
                                                                   self._user_input.fwhm)
        for inputceon, state in zip(input_ceons, init_states):
            inputceon.set_excited_state(state, self._user_input.n_exc_states_propagate_ex_param)
        self._input_ceons = input_ceons
