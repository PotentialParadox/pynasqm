from pynasqm.trajectories import Trajectories
import pynasqm.cpptraj as nasqm_cpptraj
import pytraj as pt
import pynasqm.nasqmslurm as nasqm_slurm
from pynasqm.utils import mkdir
import os

import subprocess

class AbsTrajectories(Trajectories):

    def __init__(self, user_input, input_ceon):
        self._user_input = user_input
        self._input_ceons = [input_ceon]
        self._number_trajectories = user_input.n_snapshots_gs
        self._child_root = 'nasqm_abs_'
        self._job_suffix = 'abs'
        self._parent_restart_root = 'ground_snap'
        self._number_frames_in_parent = user_input.n_mcrd_frames_gs * user_input.n_ground_runs
        self._amber_restart = False

    def _set_initial_input(self):
        input_ceon = self._input_ceons[0]
        user_input = self._user_input
        input_ceon.set_n_steps(user_input.n_steps_abs)
        input_ceon.set_n_steps_to_mcrd(user_input.n_steps_print_amcrd)
        input_ceon.set_quantum(True)
        input_ceon.set_excited_state(0, user_input.n_abs_exc)
        input_ceon.set_n_steps_to_print(user_input.n_steps_to_print_abs)
        input_ceon.set_verbosity(1)
        input_ceon.set_time_step(user_input.time_step)
        input_ceon.set_random_velocities(False)

    @staticmethod
    def restart_path(trajectory, restart):
        return "abs/traj_{}/restart_{}/snap_for_abs_t{}_r{}.rst".format(trajectory, restart, trajectory, restart)

    def start_from_mmground(self):
        mm_traj = "mmground/nasqm_ground.nc"
        self._check_trajins([mm_traj])
        self._create_directories()
        restart_step = int(self._number_frames_in_parent / self._number_trajectories)
        nasqm_cpptraj.create_restarts(amber_inputfile=mm_traj,
                                      output=self._parent_restart_root, step=restart_step)
        self._move_restarts()

    def start_from_restart(self):
        self._create_directories()
        self._copy_from_restart()

    def _copy_from_restart(self):
        restart = self._user_input.restart_attempt
        for traj in range(1, self._number_trajectories+1):
            source_path = "abs/traj_{}/restart_{}/snap_for_abs_t{}_r{}.rst".format(traj,
                                                                                   restart-1,
                                                                                   traj,
                                                                                   restart)
            if not os.path.isfile(source_path):
                subprocess.call(['touch', source_path])
            output_path = "abs/traj_{}/restart_{}/snap_for_abs_t{}_r{}.rst".format(traj,
                                                                                   restart,
                                                                                   traj,
                                                                                   restart)
            subprocess.call(['cp', source_path, output_path])

    def create_restarts_from_parent(self):
        if self._user_input.restart_attempt == 0:
            self.start_from_mmground()
        else:
            self.start_from_restart()

    def _move_restarts(self):
        for i, filename in enumerate(self._initial_snaps(), start=1):
            new_resart_name = "snap_for_abs_t{}_r{}.rst".format(i, self._user_input.restart_attempt)
            directory = "abs/traj_{}/restart_{}/{}".format(i, self._user_input.restart_attempt, new_resart_name)
            subprocess.call(['mv', filename, directory])

    def _initial_snaps(self):
        if self._number_trajectories == 1:
            return ['{}'.format(self._parent_restart_root)]
        return ["{}.{}".format(self._parent_restart_root, x)
                for x in range(1, self._number_trajectories + 1)]

    def _restart_name(self, index):
        if index == -1:
            return self._parent_restart_root
        return "{}.{}".format(self._parent_restart_root, index+1)

    def _trajins(self):
        return [self.restart_path(traj, self._user_input.restart_attempt)
                for traj in range(1, self._number_trajectories+1)]

    def _create_directories(self):
        mkdir("abs")
        for i in range(1, self._number_trajectories + 1):
            directory = "abs/traj_{}".format(i)
            restart_directory = "abs/traj_{}/restart_{}".format(i, self._user_input.restart_attempt)
            nmr_directory = "abs/traj_{}/nmr".format(i)
            mkdir(directory)
            mkdir(restart_directory)
            mkdir(nmr_directory)

    def hpc_coordinate_files(self):
        return ["snap_for_abs_t${{ID}}_r{}.rst".format(self._user_input.restart_attempt)]

    def pc_coordinate_files(self):
        return ["snap_for_abs_t{}_r{}.rst".format(i, self._user_input.restart_attempt)
                for i in range(1, self._number_trajectories+1)]

    def _nmrdirs(self):
        return ["abs/traj_{}/nmr".format(i) for i in range(1, self._number_trajectories+1)]


