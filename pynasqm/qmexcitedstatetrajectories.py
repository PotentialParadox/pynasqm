import os
import numpy as np
from collections import namedtuple
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
        input_ceon.set_time_step(user_input.time_step)
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
        if self.doing_laser_excitation():
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

    def get_sm_states(self):
        pulse_pump_outputs = ["pulse_pump/traj_{0}/restart_0/muab.out".format(traj)
                              for traj in self.traj_indices()]
        nstates = self._user_input.n_exc_states_propagate_ex_param
        sms = [self.find_sm(filename, nstates) for filename in pulse_pump_outputs]
        print("PulsePump Sm States:")
        with open('pump_pulse_states.txt', 'w') as fout:
            fout.write("{:15s}{:15s}\n".format("Traj","Init State"))
            for i, s in enumerate(sms):
                fout.write("{:<15d}{:<15d}\n".format(i+1, s))
        return sms

    @staticmethod
    def read_muab_line(line):
        MuabTuple = namedtuple('MuabTuple', 'init_state, fin_state, energy, x, y, z, strength')
        return MuabTuple(line[0], line[1], line[2], line[3], line[4], line[5], line[6])

    def read_muab(self, muab_file):
        muab_data = np.loadtxt(muab_file)
        return [self.read_muab_line(line) for line in muab_data]

    def muab_from_s1(self, filename):
        data = self.read_muab(filename)
        return [x for x in data if x.init_state == 1]

    def find_sm(self, filename, nstates):
        from_s1 = self.muab_from_s1(filename)
        strengths = [x.strength for x in from_s1]
        tentative_sm_index = strengths.index(max(strengths))
        sm_state = None
        if self.satisfies_pulse_pump_criteria(from_s1[tentative_sm_index]):
            sm_state = tentative_sm_index + 1
        else:
            sm_state = -1
        return sm_state

    def satisfies_pulse_pump_criteria(self, muab_line):
        return muab_line.strength > self._user_input.pump_pulse_min_strength \
            and muab_line.energy >= self._user_input.pump_pulse_min_energy \
            and muab_line.energy <= self._user_input.pump_pulse_max_energy

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
