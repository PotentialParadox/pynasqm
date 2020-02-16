import os
from random import randint
from pynasqm.utils import copy_files, mkdir
from pynasqm.fluorescencetrajectories import FluTrajectories
import pynasqm.cpptraj as nasqm_cpptraj
from pynasqm.initialexcitedstates import get_n_initial_states_w_laser_energy_and_fwhm
from pynasqm.inputceon import InputCeon

class PulsePump(FluTrajectories):

    def __init__(self, user_input, input_ceon):
        self._user_input = user_input
        self._input_ceons = [input_ceon]
        self._number_trajectories = user_input.n_snapshots_ex
        self._child_root = 'nasqm_pulse_pump_'
        self._job_suffix = 'pulse_pump'
        self._parent_restart_root = 'nasqm_qmground_'
        self._amber_restart = True

    def _restart_name(self, index):
        if index == -1:
            return "{}{}.rst".format(self._parent_restart_root, 1)
        return "{}{}.rst".format(self._parent_restart_root, index+1)

    def _set_initial_input(self):
        input_ceon = self._input_ceons[0]
        user_input = self._user_input
        input_ceon.set_quantum(True)
        input_ceon.set_n_steps(0)
        input_ceon.set_n_steps_to_mcrd(user_input.n_steps_print_emcrd)
        input_ceon.set_excited_state(1, user_input.n_exc_states_propagate_ex_param)
        input_ceon.set_n_steps_to_print(user_input.n_steps_to_print_exc)
        input_ceon.set_verbosity(1)
        input_ceon.set_time_step(user_input.time_step)
        input_ceon.set_random_velocities(False)
        input_ceon.set_istully(False, user_input.qsteps)
        input_ceon.calc_transition_dipoles(True)
        user_input.walltime="01:00:00" # This calculation does not take a lot of time

    def create_restarts_from_parent(self, override=False):
        self._create_directories()
        self.start_from_qmground(override)

    def create_inputceon_copies(self):
        inputceons = []
        attempt = self._user_input.restart_attempt
        job = self._job_suffix
        mkdir("{}".format(job))
        for index in range(1, self._number_trajectories+1):
            file_name = "{}t{}_r{}.in".format(self._child_root, index, attempt)
            mkdir("{}/traj_{}".format(job, index))
            mkdir("{}/traj_{}/restart_{}".format(job, index, attempt))
            directory = "{}/traj_{}/restart_{}".format(job, index, attempt)
            inputceons.append(self._input_ceons[0].copy(directory, file_name))
        inputceons = self.set_nexmd_seed(inputceons)
        self._input_ceons = inputceons

    def _update_nmr_info(self):
        pass
