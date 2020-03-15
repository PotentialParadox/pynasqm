from pynasqm.trajectories.trajectories import Trajectories
import pynasqm.cpptraj as nasqm_cpptraj
import pytraj as pt
import pynasqm.nasqmslurm as nasqm_slurm
from pynasqm.utils import mkdir
from pynasqm.trajectories.qmground import QmGround
import os

import subprocess

class QmGroundTrajectories(Trajectories):

    def __init__(self, user_input, input_ceon):
        self.user_input = user_input
        self.input_ceons = [input_ceon]
        self.number_trajectories = user_input.n_snapshots_qmground
        self.child_root = 'nasqm_qmground_'
        self.job_suffix = 'qmground'
        self.parent_restart_root = 'ground_snap'
        self.number_frames_in_parent = user_input.n_mcrd_frames_per_run_gs * user_input.n_ground_runs
        self.amber_restart = False
        self.traj_data = QmGround(user_input, input_ceon)

    def set_initial_input(self):
        input_ceon = self.input_ceons[0]
        user_input = self.user_input
        input_ceon.set_n_steps(user_input.n_steps_per_run_qmground)
        input_ceon.set_n_steps_to_mcrd(user_input.n_steps_print_qmgmcrd)
        input_ceon.set_quantum(True)
        input_ceon.set_excited_state(0, user_input.n_qmground_exc)
        input_ceon.set_n_steps_to_print(user_input.n_steps_to_print_qmground)
        input_ceon.set_verbosity(1)
        input_ceon.set_time_step(user_input.qmground_time_step)
        input_ceon.set_random_velocities(False)
        input_ceon.calc_transition_dipoles(False)
        input_ceon.set_istully(False, 0)

    def isrestarting(self):
        return self.user_input.restart_attempt < self.user_input.n_qmground_runs - 1

    def islastrun(self):
        return not self.isrestarting()

    # def start_from_mmground(self):
    #     mm_traj = "mmground/nasqm_ground.nc"
    #     self.check_trajins([mm_traj])
    #     restart_step = int(self.number_frames_in_parent / self.number_trajectories)
    #     nasqm_cpptraj.create_restarts(amber_inputfile=mm_traj,
    #                                   output=self.parent_restart_root, step=restart_step)
    #     self.move_restarts()

    # def create_restarts_from_parent(self, override=True):
    #     self.create_directories()
    #     if self.user_input.restart_attempt == 0:
    #         self.start_from_mmground()
    #     else:
    #         self.start_from_restart(override)


    def initial_snaps(self):
        if self.number_trajectories == 1:
            return ['{}'.format(self.parent_restart_root)]
        return ["{}.{}".format(self.parent_restart_root, x)
                for x in range(1, self.number_trajectories + 1)]

    def restart_name(self, index):
        if index == -1:
            return self.parent_restart_root
        return "{}.{}".format(self.parent_restart_root, index+1)


    def hpc_coordinate_files(self):
        return ["snap_for_qmground_t${{ID}}_r{}.rst".format(self.user_input.restart_attempt)]

    def pc_coordinate_files(self):
        return ["snap_for_qmground_t{}_r{}.rst".format(i, self.user_input.restart_attempt)
                for i in range(1, self.number_trajectories+1)]

    def nmrdirs(self):
        return ["qmground/traj_{}/nmr".format(i) for i in range(1, self.number_trajectories+1)]


