from pynasqm.trajectories import Trajectories
import pynasqm.cpptraj as nasqm_cpptraj
import subprocess

class AbsTrajectories(Trajectories):

    def __init__(self, user_input, input_ceon):
        self._user_input = user_input
        self._input_ceons = [input_ceon]
        self._number_trajectories = user_input.n_snapshots_gs
        self._child_root = 'nasqm_abs_'
        self._job_suffix = '_a_'
        self._parent_restart_root = 'ground_snap'
        self._parent_trajectory_root = 'nasqm_ground'
        self._number_frames_in_parent = user_input.n_mcrd_frames_gs
        self._amber_restart = False

    def _create_restarts_from_parent(self):
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
        trajins = []
        for i in range(1, self._number_trajectories+1):
            trajins.append("{}/ground_snap.{}".format(i, i))
        return trajins
