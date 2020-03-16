import os
import numpy as np
from collections import namedtuple
from random import randint
from pynasqm.utils import copy_files, mkdir
from pynasqm.qmexcitedstatetrajectories import QmExcitedStateTrajectories
import pynasqm.cpptraj as nasqm_cpptraj
from pynasqm.initialexcitedstates import get_n_initial_states_w_laser_energy_and_fwhm
from pynasqm.inputceon import InputCeon
from pynasqm.trajectories.ppump import PPump

class PulsePump(QmExcitedStateTrajectories):

    def __init__(self, user_input, input_ceon):
        self.user_input = user_input
        self.input_ceons = [input_ceon]
        self.number_trajectories = user_input.n_snapshots_ex
        self.child_root = 'nasqm_pulse_pump_'
        self.job_suffix = 'pulse_pump'
        self.parent_restart_root = 'nasqm_qmground_'
        self.amber_restart = True
        self.traj_data = PPump(user_input, input_ceon)

    def _restart_name(self, index):
        if index == -1:
            return "{}{}.rst".format(self.parent_restart_root, 1)
        return "{}{}.rst".format(self.parent_restart_root, index+1)

    def _set_initial_input(self):
        input_ceon = self.input_ceons[0]
        user_input = self.user_input
        input_ceon.set_quantum(True)
        input_ceon.set_n_steps(0)
        input_ceon.set_n_steps_to_mcrd(user_input.n_steps_print_emcrd)
        n_states_to_prop = user_input.n_exc_states_propagate_ex_param-1
        input_ceon.set_excited_state(1, n_states_to_prop)
        input_ceon.set_n_steps_to_print(user_input.n_steps_to_print_exc)
        input_ceon.set_verbosity(1)
        input_ceon.set_time_step(user_input.qmground_time_step)
        input_ceon.set_random_velocities(False)
        input_ceon.set_istully(False, user_input.qsteps)
        input_ceon.calc_transition_dipoles(True)
        user_input.walltime="01:00:00" # This calculation does not take a lot of time

    def create_restarts_from_parent(self, override=False):
        self.create_directories()
        self.start_from_qmground(override)

    def create_inputceon_copies(self):
        inputceons = []
        attempt = self.user_input.restart_attempt
        job = self.job_suffix
        mkdir("{}".format(job))
        for index in range(1, self.number_trajectories+1):
            file_name = "{}t{}_r{}.in".format(self.child_root, index, attempt)
            mkdir("{}/traj_{}".format(job, index))
            mkdir("{}/traj_{}/restart_{}".format(job, index, attempt))
            directory = "{}/traj_{}/restart_{}".format(job, index, attempt)
            inputceons.append(self.input_ceons[0].copy(directory, file_name))
        inputceons = self.set_nexmd_seed(inputceons)
        self.input_ceons = inputceons

    def _update_nmr_info(self):
        pass

    def write_pulse_pump_states(self):
        pulse_pump_outputs = ["pulse_pump/traj_{0}/restart_0/muab.out".format(traj)
                              for traj in self.traj_indices()]
        nstates = self.user_input.n_exc_states_propagate_ex_param
        sms = [self.find_sm(filename, nstates) for filename in pulse_pump_outputs]
        with open('pulse_pump_states.txt', 'w') as fout:
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
        print(f"Collecting from {filename}")
        if not os.path.exists(filename):
            return -1
        from_s1 = self.muab_from_s1(filename)
        strengths = [x.strength for x in from_s1]
        tentative_sm_index = strengths.index(max(strengths))
        sm_state = None
        if not self.satisfies_pulse_pump_criteria(from_s1[tentative_sm_index]):
            return -1
        return tentative_sm_index + 1

    def satisfies_pulse_pump_criteria(self, muab_line):
        return muab_line.strength > self.user_input.pump_pulse_min_strength \
            and muab_line.energy >= self.user_input.pump_pulse_min_energy \
            and muab_line.energy <= self.user_input.pump_pulse_max_energy
