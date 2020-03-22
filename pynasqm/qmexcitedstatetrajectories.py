import os
from random import randint
from pynasqm.utils import copy_files, mkdir
from pynasqm.trajectories import Trajectories
import pynasqm.cpptraj as nasqm_cpptraj
from pynasqm.initialexcitedstates import get_n_initial_states_w_laser_energy_and_fwhm
from pynasqm.inputceon import InputCeon

class QmExcitedStateTrajectories(Trajectories):

    def __init__(self, user_input, input_ceon):
        self._user_input = user_input
        self._input_ceons = [input_ceon]
        self._number_trajectories = user_input.n_snapshots_ex
        self._child_root = 'nasqm_qmexcited_'
        self._job_suffix = 'qmexcited'
        self._parent_restart_root = 'nasqm_qmground_'
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
        input_ceon.set_n_steps(user_input.n_steps_per_run_exc)
        input_ceon.set_n_steps_to_mcrd(user_input.n_steps_print_emcrd)
        input_ceon.set_excited_state(user_input.exc_state_init_ex_param,
                                     user_input.n_exc_states_propagate_ex_param)
        input_ceon.set_n_steps_to_print(user_input.n_steps_to_print_exc)
        input_ceon.set_verbosity(1)
        input_ceon.set_time_step(user_input.exc_time_step)
        input_ceon.set_random_velocities(False)
        input_ceon.calc_transition_dipoles(False)
        input_ceon.set_istully(user_input.is_tully, user_input.qsteps)

    @staticmethod
    def test_for_qmground():
        if not os.path.isdir("qmground"):
            raise AssertionError("qmground directory not found.\n"\
                                 "Did you run the QM ground-state trajectories?\n")

    def isrestarting(self):
        return self._user_input.restart_attempt < self._user_input.n_exc_runs - 1

    def islastrun(self):
        return not self.isrestarting()

    def start_from_qmground(self, override):
        self.copy_restarts_from_qmground(override)
        if self._user_input.restrain_solvents:
            self.copy_nmr_from_qmground()

    def copy_nmr_from_qmground(self):
        source_files = ["qmground/traj_{}/nmr/rst_{}.dist".format(t, t) for t in self.traj_indices()]
        output_files = ["qmexcited/traj_{}/nmr/rst_{}.dist".format(t, t) for t in self.traj_indices()]
        copy_files(source_files, output_files)
        source_files = ["qmground/traj_{}/nmr/closest_{}.txt".format(t, t) for t in self.traj_indices()]
        output_files = ["qmexcited/traj_{}/nmr/closest_{}.txt".format(t, t) for t in self.traj_indices()]
        copy_files(source_files, output_files)

    def copy_restarts_from_qmground(self, override):
        self.test_for_qmground()
        r = self._user_input.n_qmground_runs - 1
        source_files = ["qmground/traj_{}/restart_{}/snap_for_qmground_t{}_r{}.rst".format(t, r, t, r+1)
                        for t in self.traj_indices()]
        output_files = ["{1}/traj_{0}/restart_0/snap_for_{1}_t{0}_r0.rst".format(t, self._job_suffix)
                        for t in self.traj_indices()]
        copy_files(source_files, output_files, force=override)


    def create_restarts_from_parent(self, override=False):
        self._create_directories()
        if self._user_input.restart_attempt == 0:
            self.start_from_qmground(override)
        else:
            self.start_from_restart(override)

    def set_excited_states(self, input_ceons):
        print("Setting Initial Excited States")
        if self._user_input.restart_attempt > 0:
            print("From Restarts")
            r_attempt = self._user_input.restart_attempt
            init_states = [self.get_state_from_restart(r_attempt, traj_id)
                           for traj_id in self.traj_indices()]
        elif self.doing_laser_excitation():
            init_states = get_n_initial_states_w_laser_energy_and_fwhm(self._number_trajectories,
                                                                       'spectra_abs.input',
                                                                       self._user_input.laser_energy,
                                                                       self._user_input.fwhm)
        elif self._user_input.is_pulse_pump:
            init_states = self.get_sm_states()
        else:
            init_states = [self._user_input.exc_state_init_ex_param for _ in range(self._number_trajectories)]
        for inputceon, state in zip(input_ceons, init_states):
            inputceon.set_excited_state(state, self._user_input.n_exc_states_propagate_ex_param)

        print("Finished Setting Initial Excited States")
        return input_ceons

    def get_state_from_restart(self, restart_attempt, traj_id):
        refference_restart = restart_attempt - 1
        coeffn_file = f"qmexcited/traj_{traj_id}/restart_{refference_restart}/coeff-n.out"
        if os.path.isfile(coeffn_file):
            coeffn_data = open(coeffn_file, 'r').readlines()
            return int(coeffn_data[-1].split()[0])
        return -1

    def get_sm_states(self):
        pulse_pump_text = open("pulse_pump_states.txt").readlines()
        state_data = pulse_pump_text[1:]
        init_states = [int(s.split()[1]) for s in state_data]
        return init_states

    def set_nexmd_seed(self, inputceons):
        print("Setting NEXMD Random Seeds")
        random_seeds = [randint(1,10000) for i in range(len(inputceons))]
        for inputceon, seed in zip(inputceons, random_seeds):
            inputceon.set_nexmd_seed(seed)
        return inputceons

    def _nmrdirs(self):
        return ["qmexcited/traj_{}/nmr".format(i) for i in range(1, self._number_trajectories+1)]

    @staticmethod
    def is_atleast(min_value, test):
        if min_value is None:
            return True
        return test >= min_value

    @staticmethod
    def is_atmost(max_value, test):
        if max_value is None:
            return True
        return test >= max_value

    def satisfies_pulse_pump(self, restraints, muab_for_sm):
        return is_atleast(restraints.min_energy, muab_for_sm.energy) \
            and is_atmost(restraints.max_energy, muab_for_sm.energy) \
            and is_atleast(restraints.min_strength, muab_for_sm.strength)
