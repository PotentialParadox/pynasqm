from pynasqm.trajectories import Trajectories
import pynasqm.cpptraj as nasqm_cpptraj

class AbsTrajectories(Trajectories):

    def __init__(self, user_input, input_ceon):
        self._user_input = user_input
        self._input_ceons = [input_ceon]
        self._number_trajectories = user_input.n_snapshots_gs
        self._child_root = 'nasqm_abs_'
        self._job_suffix = '_a_'
        self._parent_restart_root = 'ground_snap'
        self._parent_trajectory_root = 'nasqm_ground'
        self._number_frames_in_parent = user_input.n_frames_gs
        self._amber_restart = False

    def _create_restarts_from_parent(self):
        restart_step = int(self._number_frames_in_parent / self._number_trajectories)
        nasqm_cpptraj.create_restarts(amber_input=self._parent_trajectory_root,
                                      output=self._parent_restart_root, step=restart_step)


    def _restart_name(self, index):
        if index == -1:
            return self._parent_restart_root
        return "{}.{}".format(self._parent_restart_root, index+1)
