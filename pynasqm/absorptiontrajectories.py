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

    def _update_input_files(self):
        n_qm_solvents = self._user_input.number_nearest_solvents
        if n_qm_solvents > 0:
            center_mask = self._user_input.mask_for_center
            trajins = self._trajins()
            self._check_trajins(trajins)
            closest_runner = ClosestRunner(n_qm_solvents, self._number_trajectories,
                                           trajins, center_mask)
            closest_outputs = closest_runner.create_closest_outputs()
            mask_updater = SolventMaskUpdater(self._input_ceons, self._user_input, closest_outputs)
            mask_updater.update_masks()
            if self._user_input.restrain_solvents is True:
                trajins = closest_runner.get_trajins()
                parmtop = "m1.prmtop"
                restricted_atoms = self._get_list_restricted_atoms(parmtop, trajins, closest_outputs)
                distances = self._get_distances(parmtop, trajins, closest_outputs, restricted_atoms[0].nresidues)
                NMRManager(self._input_ceons, closest_outputs, restricted_atoms, distances).update()


