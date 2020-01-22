import os
from random import randint
from pynasqm.utils import copy_files, mkdir
from pynasqm.trajectories import Trajectories
import pynasqm.cpptraj as nasqm_cpptraj
from pynasqm.initialexcitedstates import get_n_initial_states_w_laser_energy_and_fwhm
from pynasqm.inputceon import InputCeon

class FluTrajectories(Trajectories):

    def __init__(self, user_input, input_ceon):
        self._user_input = user_input
        self._input_ceons = [input_ceon]
        self._number_trajectories = user_input.n_snapshots_ex
        self._child_root = 'nasqm_flu_'
        self._job_suffix = 'flu'
        self._parent_restart_root = 'nasqm_abs_'
        self._amber_restart = True

    def _restart_name(self, index):
        if index == -1:
            return "{}{}.rst".format(self._parent_restart_root, 1)
        return "{}{}.rst".format(self._parent_restart_root, index+1)

    def doing_laser_excitation(self):
        return self._user_input.exc_state_init_ex_param == -1

    def _set_initial_input(self):
        input_ceon = self._input_ceons[0]
        user_input = self._user_input
        input_ceon.set_quantum(True)
        input_ceon.set_n_steps(user_input.n_steps_exc)
        input_ceon.set_n_steps_to_mcrd(user_input.n_steps_print_emcrd)
        input_ceon.set_excited_state(user_input.exc_state_init_ex_param,
                                     user_input.n_exc_states_propagate_ex_param)
        input_ceon.set_n_steps_to_print(user_input.n_steps_to_print_exc)
        input_ceon.set_verbosity(1)
        input_ceon.set_time_step(user_input.time_step)
        input_ceon.set_random_velocities(False)
        input_ceon.set_bo(user_input.is_tully, user_input.qsteps)

    @staticmethod
    def test_for_abs():
        if not os.path.isdir("abs"):
            raise AssertionError("abs directory not found.\n"\
                                 "Did you run the ground state?\n")

    def isrestarting(self):
        return self._user_input.restart_attempt < self._user_input.n_exc_runs - 1

    def islastrun(self):
        return not self.isrestarting()

    def start_from_abs(self, override):
        self.copy_restarts_from_abs(override)
        if self._user_input.restrain_solvents:
            self.copy_nmr_from_abs()

    def copy_nmr_from_abs(self):
        source_files = ["abs/traj_{}/nmr/rst_{}.dist".format(t, t) for t in self.traj_indexes()]
        output_files = ["flu/traj_{}/nmr/rst_{}.dist".format(t, t) for t in self.traj_indexes()]
        copy_files(source_files, output_files)
        source_files = ["abs/traj_{}/nmr/closest_{}.txt".format(t, t) for t in self.traj_indexes()]
        output_files = ["flu/traj_{}/nmr/closest_{}.txt".format(t, t) for t in self.traj_indexes()]
        copy_files(source_files, output_files)

    def copy_restarts_from_abs(self, override):
        self.test_for_abs()
        r = self._user_input.n_abs_runs - 1
        source_files = ["abs/traj_{}/restart_{}/snap_for_abs_t{}_r{}.rst".format(t, r, t, r+1)
                        for t in self.traj_indexes()]
        output_files = ["{1}/traj_{0}/restart_0/snap_for_{1}_t{0}_r0.rst".format(t, self._job_suffix)
                        for t in self.traj_indexes()]
        copy_files(source_files, output_files, force=override)


    def create_restarts_from_parent(self, override=False):
        self._create_directories()
        if self._user_input.restart_attempt == 0:
            self.start_from_abs(override)
        else:
            self.start_from_restart(override)

    def set_excited_states(self, input_ceons):
        print("Setting Initial Excited States")
        if self.doing_laser_excitation():
            init_states = get_n_initial_states_w_laser_energy_and_fwhm(self._number_trajectories,
                                                                       'spectra_abs.input',
                                                                       self._user_input.laser_energy,
                                                                       self._user_input.fwhm)
        else:
            init_states = [self._user_input.exc_state_init_ex_param for _ in range(self._number_trajectories)]
        for inputceon, state in zip(input_ceons, init_states):
            inputceon.set_excited_state(state, self._user_input.n_exc_states_propagate_ex_param)
        print("Finished Setting Initial Excited States")
        return input_ceons

    def set_nexmd_seed(self, inputceons):
        print("Setting NEXMD Random Seeds")
        random_seeds = [randint(1,10000) for i in range(len(inputceons))]
        for inputceon, seed in zip(inputceons, random_seeds):
            inputceon.set_nexmd_seed(seed)
        return inputceons

    def _nmrdirs(self):
        return ["flu/traj_{}/nmr".format(i) for i in range(1, self._number_trajectories+1)]
