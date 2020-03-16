from abc import ABC, abstractmethod
import os.path
import subprocess
from os import mkdir
from pynasqm.nmr.closestrunner import ClosestRunner
from pynasqm.nmr.solventmaskupdater import SolventMaskUpdater
from pynasqm.nmr.nmrmanager import NMRManager, create_dist_file_name, toInputPath
from pynasqm.amber import Amber
import pynasqm.nasqmslurm as nasqm_slurm
from pynasqm.nmr.restrictedatoms import RestrictedAtoms
from pynasqm.nmr.trajdistance import TrajDistance
from pynasqm.nmr.closestreader import ClosestReader
from pynasqm.utils import mkdir, copy_file, is_empty_file
from pynasqm.cpptraj import create_restarts
from pynasqm.trajectories.create_restarts import create_restarts_from_parent
from pynasqm.trajectories.set_initial_input import set_initial_input
from pynasqm.trajectories.create_inputceon_copies import create_inputceon_copies
from pynasqm.nmr.update_nmr_info import update_nmr_info
import pytraj as pt

class Trajectories(ABC):

    def __init__(self, user_input, input_ceon, number_trajectories=1):
        self.user_input = user_input
        self.input_ceons = [input_ceon]
        self.number_trajectories = number_trajectories
        self.child_root = "undefined_root"
        self.job_suffix = "undefined_job_suffix"
        self.parent_restart_root = "undefined_parent_root"
        self.amber_restart = True
        self.traj_data = None

    def __str__(self):
        print_value = ""\
            f"Traj_Data Info:\n"\
            f"Class: {self.job_suffix}:\n"\
            f"Number input_ceons: {len(self.input_ceons)}\n"\
            f"Number trajectories: {self.number_trajectories}\n"
        return print_value

    def run(self):
        self.set_initial_input()
        self.gen_inputfiles()
        self.print_header("Running {} Dynamics".format(self.job_suffix))
        (amber, slurm) = self.prepareScript()
        self.runDynamics(amber, slurm)

    def gen_inputfiles(self):
        self.create_restarts_from_parent()
        self.create_inputceon_copies()
        if self.user_input.number_nearest_solvents > 0:
            self.update_nmr_info()

    @abstractmethod
    def islastrun(self):
        pass

    @staticmethod
    def print_header(header):
        print(50*"*")
        print(15 * " " + header)
        print(50*"*")

    def create_restarts_from_parent(self, override=True):
        create_restarts_from_parent(self.traj_data, 0, override=True)

    def create_inputceon_copies(self):
        create_inputceon_copies(self.traj_data)
        self.input_ceons = self.traj_data.input_ceons


    def set_excited_states(self, inputceons):
        return inputceons

    @abstractmethod
    def nmrdirs(self):
        pass

    def should_update_nmr(self):
        return (self.user_input.restart_attempt == 0
                and self.job_suffix == "qmground"
                and self.user_input.restrain_solvents is True
                and self.user_input.number_nearest_solvents > 0)

    def update_nmr_info(self):
        update_nmr_info(self.traj_data)


    def trajins(self):
        return [self.restart_path(traj, self.user_input.restart_attempt)
                for traj in range(1, self.number_trajectories+1)]

    def set_initial_input(self):
        set_initial_input(self.traj_data)

    def runDynamics(self, amber, slurm_file):
        if self.user_input.is_hpc:
            nasqm_slurm.run_nasqm_slurm_file(slurm_file)
        else:
            amber.run_amber(number_processors=self.user_input.processors_per_node,
                            is_ground_state=False)

    def hpc_coordinate_files(self):
        return ["snap_for_{}_t${{ID}}_r{}.rst".format(self.job_suffix,
                                                      self.user_input.restart_attempt)]

    def pc_coordinate_files(self):
        return ["snap_for_{}_t{}_r{}.rst".format(self.job_suffix, traj, self.user_input.restart_attempt)
                for traj in range(1, self.number_trajectories+1)]

    def coordinate_files(self):
        if self.user_input.is_hpc:
            return self.hpc_coordinate_files()
        return self.pc_coordinate_files()

    def prmtop_files(self):
        if self.user_input.is_hpc:
            return ["m1.prmtop"]
        return ["m1.prmtop"] * self.number_trajectories

    def traj_indices(self):
        return range(1, self.number_trajectories+1)

    def output_directories(self):
        restart = self.user_input.restart_attempt
        job = self.job_suffix
        return ["{}/traj_{}/restart_{}".format(job, traj, restart)
                for traj in self.traj_indices()]

    def create_amber(self):
        amber = Amber()
        roots = None
        restart_attempt = self.user_input.restart_attempt
        if self.user_input.is_hpc:
            roots = ["{}t${{ID}}_r{}".format(self.child_root, restart_attempt)]
            restart_files = ["snap_for_{}_t${{ID}}_r{}.rst".format(self.job_suffix, restart_attempt+1)]
            amber.prmtop_files = ["m1.prmtop"]
        else:
            roots = ["{}t{}_r{}".format(self.child_root, i, restart_attempt)
                     for i in range(1, self.number_trajectories+1)]
            restart_files = ["snap_for_{}_t{}_r{}.rst".format(self.job_suffix, i, restart_attempt+1)
                             for i in range(1, self.number_trajectories+1)]
            amber.prmtop_files = ["m1.prmtop"] * self.number_trajectories
        amber.input_roots = roots
        amber.output_roots = roots
        amber.restart_files = restart_files
        amber.export_roots = roots
        amber.coordinate_files = self.coordinate_files()
        amber.prmtop_files = self.prmtop_files()
        amber.directories = self.output_directories()
        return amber

    def create_slurm(self, amber):
        if self.user_input.is_hpc:
            job_name = self.user_input.job_name + self.job_suffix
            directory = "{}/traj_${{ID}}/restart_{}".format(self.job_suffix, self.user_input.restart_attempt)
            slurm_file = nasqm_slurm.slurm_trajectory_files(self.user_input, amber,
                                                             job_name, self.job_suffix, directory)
        else:
            slurm_file = None
        return slurm_file

    def prepareScript(self):
        amber = self.create_amber()
        slurm_files = self.create_slurm(amber)
        return amber, slurm_files

    @abstractmethod
    def restart_name(self, index):
        pass

    def trajectory_name(self, index):
        if index == -1:
            index = 0
        return "{}{}".format(self.child_root, index+1)


    def restart_path(self, trajectory, restart):
        return "{}/traj_{}/restart_{}/snap_for_{}_t{}_r{}.rst".format(self.job_suffix,
                                                                      trajectory, restart,
                                                                      self.job_suffix,
                                                                      trajectory, restart)

