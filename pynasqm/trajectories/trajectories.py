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
from pynasqm.trajectories.create_restarts import create_restarts_from_parent
from pynasqm.trajectories.set_initial_input import set_initial_input
from pynasqm.trajectories.create_inputceon_copies import create_inputceon_copies
from pynasqm.nmr.update_nmr_info import update_nmr_info
from pynasqm.trajectories.create_amber import create_amber
from pynasqm.trajectories.create_slurm import create_slurm
from pynasqm.trajectories.copy_bondorder_connectdat import copy_bondorder_connectdat
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
        set_initial_input(self.traj_data)
        self.gen_inputfiles()
        self.print_header("Running {} Dynamics".format(self.job_suffix))
        (amber, slurm) = self.prepareScript()
        self.runDynamics(amber, slurm)

    def gen_inputfiles(self):
        create_restarts_from_parent(self.traj_data, 0, override=True)
        create_inputceon_copies(self.traj_data)
        copy_bondorder_connectdat(self.traj_data)
        self.input_ceons = self.traj_data.input_ceons
        if self.user_input.number_nearest_solvents > 0:
            update_nmr_info(self.traj_data)


    @staticmethod
    def print_header(header):
        print(50*"*")
        print(15 * " " + header)
        print(50*"*")

    def runDynamics(self, amber, slurm_file):
        if self.user_input.is_hpc:
            nasqm_slurm.run_nasqm_slurm_file(slurm_file)
        else:
            amber.run_amber(number_processors=self.user_input.processors_per_node,
                            is_ground_state=False)

    def prepareScript(self):
        amber = create_amber(self.traj_data)
        slurm_files = create_slurm(self.traj_data, amber)
        return amber, slurm_files



