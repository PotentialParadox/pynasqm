from pynasqm.amber import Amber
from pynasqm.trajectories.utils import traj_indices
from pynasqm.trajectories.amber_restart_files import amber_pc_restart_files, amber_hpc_restart_files
from pynasqm.trajectories.getambercoordinatefiles import get_coordinate_files
from pynasqm.trajectories.select_working_directories import select_working_directories
from pynasqm.trajectories.select_pc_roots import select_pc_roots

def create_amber(traj_data):
    amber = Amber()
    roots = None
    restart_attempt = traj_data.user_input.restart_attempt
    if traj_data.user_input.is_hpc:
        roots = ["{}t${{ID}}_r{}".format(traj_data.child_root, restart_attempt)]
        restart_files = amber_hpc_restart_files(traj_data, restart_attempt)
        amber.prmtop_files = ["m1.prmtop"]
    else:
        roots = select_pc_roots(traj_data, restart_attempt)
        restart_files = amber_pc_restart_files(traj_data, restart_attempt)
        amber.prmtop_files = ["m1.prmtop"] * traj_data.number_trajectories
    amber.input_roots = roots
    amber.output_roots = roots
    amber.restart_files = restart_files
    amber.export_roots = roots
    amber.coordinate_files = get_coordinate_files(traj_data)
    amber.prmtop_files = prmtop_files(traj_data, nroots = len(roots))
    amber.directories = select_working_directories(traj_data)
    return amber

def prmtop_files(traj_data, nroots):
    if traj_data.user_input.is_hpc:
        return ["m1.prmtop"]
    return ["m1.prmtop"] * nroots


