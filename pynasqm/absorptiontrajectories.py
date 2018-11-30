from pynasqm.trajectories import Trajectories
import pynasqm.cpptraj as nasqm_cpptraj
import pynasqm.nasqmslurm as nasqm_slurm
import os

import subprocess

class AbsTrajectories(Trajectories):

    def __init__(self, user_input, input_ceon):
        self._user_input = user_input
        self._input_ceons = [input_ceon]
        self._number_trajectories = user_input.n_snapshots_gs
        self._child_root = 'nasqm_abs_'
        self._job_suffix = 'Abs'
        self._parent_restart_root = 'ground_snap'
        self._parent_trajectory_root = 'nasqm_ground'
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

    def create_restarts_from_parent(self):
        if self._user_input.restart_attempt == 0:
            self._check_trajins(["nasqm_ground.nc"])
            self._create_directories()
            restart_step = int(self._number_frames_in_parent / self._number_trajectories)
            nasqm_cpptraj.create_restarts(amber_input=self._parent_trajectory_root,
                                        output=self._parent_restart_root, step=restart_step)
            self._move_restarts()

    def _move_restarts(self):
        for i, filename in enumerate(self._initial_snaps(), start=1):
            directory = "{}/{}.{}".format(i, self._parent_restart_root, i)
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
        attempt = self._user_input.restart_attempt
        if attempt == 0:
            return ["{}/ground_snap.{}".format(i, i) for i in range(1, self._number_trajectories+1)]
        return ["{}/nasqm_abs_r{}_t{}.rst".format(i, attempt, i)
                for i in range(1, self._number_trajectories+1)]

    def _create_directories(self):
        for i in range(1, self._number_trajectories + 1):
            directory = "{}".format(i)
            if not os.path.exists(directory):
                os.mkdir(directory)
