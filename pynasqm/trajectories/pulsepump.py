import os
import numpy as np
from collections import namedtuple
from random import randint
from pynasqm.utils import copy_files, mkdir
from pynasqm.trajectories.qmexcitedstatetrajectories import QmExcitedStateTrajectories
import pynasqm.cpptraj as nasqm_cpptraj
from pynasqm.initialexcitedstates import get_n_initial_states_w_laser_energy_and_fwhm
from pynasqm.inputceon import InputCeon
from pynasqm.trajectories.ppump import PPump
from pynasqm.trajectories.utils import traj_indices

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


    def _update_nmr_info(self):
        pass

    def write_pulse_pump_states(self):
        pulse_pump_outputs = ["pulse_pump/traj_{0}/restart_0/muab.out".format(traj)
                              for traj in traj_indices(self)]
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
