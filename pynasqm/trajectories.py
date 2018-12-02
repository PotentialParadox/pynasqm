from abc import ABC, abstractmethod
import os.path
from os import mkdir
from pynasqm.closestrunner import ClosestRunner
from pynasqm.solventmaskupdater import SolventMaskUpdater
from pynasqm.nmrmanager import NMRManager
from pynasqm.amber import Amber
import pynasqm.nasqmslurm as nasqm_slurm
from pynasqm.restrictedatoms import RestrictedAtoms
from pynasqm.trajdistance import TrajDistance
from pynasqm.closestreader import ClosestReader

class Trajectories(ABC):

    def __init__(self, user_input, input_ceon, number_trajectories=1):
        self._user_input = user_input
        self._input_ceons = [input_ceon]
        self._number_trajectories = number_trajectories
        self._child_root = "undefined_root"
        self._job_suffix = "undefined_job_suffix"
        self._parent_restart_root = "undefined_parent_root"
        self._amber_restart = True

    def run(self):
        self._set_initial_input()
        self.create_restarts_from_parent()
        self.create_inputceon_copies()
        self._update_input_files()
        self._print_header("Running Dynamics")
        (amber, slurm) = self.prepareDynamics()
        self.runDynamics(amber, slurm)

    @staticmethod
    def _print_header(header):
        print(50*"*")
        print(15 * " " + header)
        print(50*"*")

    def create_restarts_from_parent(self):
        pass

    def create_inputceon_copies(self):
        input_ceons = []
        attempt = self._user_input.restart_attempt
        for index in range(1, self._number_trajectories+1):
            file_name = "{}r{}_t{}.in".format(self._child_root, attempt, index)
            input_ceons.append(self._input_ceons[0].copy("{}/".format(index), file_name))
        self._input_ceons = input_ceons

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

    def _get_distances(self, parmtop, trajins, closest_outputs, nresidues):
        center_mask = self._user_input.mask_for_center
        added_buffer = 0.0
        list_distances = []
        for traj in range(self._number_trajectories):
            residues = [":{}".format(x) for x in ClosestReader(closest_outputs[traj]).residues]
            trajdist = TrajDistance(parmtop, center_mask)
            distances = [trajdist(trajins[traj], residue, traj) + added_buffer for residue in residues]
            maxdistance = max(distances)
            newdistances = [maxdistance for _ in distances]
            distances = newdistances
            far_distances = [-maxdistance for _ in range(nresidues-len(distances)-1)]
            distances = distances + far_distances
            list_distances.append(distances)
        return list_distances

    @staticmethod
    def _check_trajins(trajins):
        for trajin in trajins:
            if not os.path.isfile(trajin):
                raise RuntimeError("{} was not found, make sure you ran the previous step: \n"\
                                   "ground_state->absorption->fluorescence".format(trajin))

    def _get_list_restricted_atoms(self, parmtop, trajins, closest_outputs):
        center_mask = self._user_input.mask_for_center
        list_restricted_atoms = []
        for traj in range(self._number_trajectories):
            print("Generating restricted atoms list for traj {}".format(traj+1))
            list_restricted_atoms.append(RestrictedAtoms(parmtop, trajins[traj], center_mask,
                                                         closest_outputs[traj]))
        return list_restricted_atoms

    @abstractmethod
    def _trajins(self):
        pass

    def _set_initial_input(self):
        pass

    def runDynamics(self, amber, slurm_files):
        if self._user_input.is_hpc:
            nasqm_slurm.run_nasqm_slurm_files(slurm_files)
        else:
            amber.run_amber(number_processors=self._user_input.processors_per_node,
                            is_ground_state=False)

    @abstractmethod
    def hpc_coordinate_files(self, attempt):
        pass

    @abstractmethod
    def pc_coordinate_files(self, attempt):
        pass

    def coordinate_files(self, attempt):
        if self._user_input.is_hpc:
            return self.hpc_coordinate_files(attempt)
        return self.pc_coordinate_files(attempt)

    def prmtop_files(self):
        if self._user_input.is_hpc:
            return ["m1.prmtop"]
        return ["m1.prmtop"] * self._number_trajectories

    def create_amber(self):
        amber = Amber()
        attempt = self._user_input.restart_attempt
        roots = None
        if self._user_input.is_hpc:
            roots = ["{}r{}_t${{ID}}".format(self._child_root, attempt)]
            amber.prmtop_files = ["m1.prmtop"]
        else:
            roots = ["{}r{}_t{}".format(self._child_root, attempt, i)
                     for i in range(1, self._number_trajectories+1)]
            amber.prmtop_files = ["m1.prmtop"] * self._number_trajectories
        amber.input_roots = roots
        amber.output_roots = roots
        amber.restart_roots = roots
        amber.export_roots = roots
        amber.coordinate_files = self.coordinate_files(attempt)
        amber.prmtop_files = self.prmtop_files()
        return amber

    def create_slurm(self, amber):
        if self._user_input.is_hpc:
            job_name = self._user_input.job_name + self._job_suffix
            slurm_files = nasqm_slurm.slurm_trajectory_files(self._user_input, amber,
                                                             job_name, self._number_trajectories)
        else:
            slurm_files = None
        return slurm_files

    def prepareDynamics(self):
        amber = self.create_amber()
        slurm_files = self.create_slurm(amber)
        return amber, slurm_files

    @abstractmethod
    def _restart_name(self, index):
        pass

    def _trajectory_name(self, index):
        if index == -1:
            index = 0
        return "{}{}".format(self._child_root, index+1)
