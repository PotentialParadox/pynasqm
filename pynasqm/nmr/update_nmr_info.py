from functools import singledispatch
from pynasqm.trajectories.qmground import QmGround
from pynasqm.nmr.closestrunner import ClosestRunner
from pynasqm.nmr.solventmaskupdater import SolventMaskUpdater
from pynasqm.nmr.restrictedatoms import RestrictedAtoms
from pynasqm.nmr.get_nmrdirs import get_nmrdirs
from pynasqm.nmr.get_distances import get_distances
from pynasqm.nmr.nmrmanager import NMRManager, toInputPath, create_dist_file_name

def update_nmr_info(traj_data):
    n_qm_solvents = traj_data.user_input.number_nearest_solvents
    nmrdirs = get_nmrdirs(traj_data)
    center_mask = traj_data.user_input.mask_for_center
    trajins = get_trajins(traj_data)
    # self.check_trajins(trajins)
    closest_runner = ClosestRunner(n_qm_solvents, traj_data.number_trajectories,
                                   trajins, center_mask, nmrdirs)
    closest_outputs = closest_runner.create_closest_outputs(run=should_update_nmr(traj_data))
    mask_updater = SolventMaskUpdater(traj_data.input_ceons, traj_data.user_input, closest_outputs)
    mask_updater.update_masks()
    trajins = closest_runner.get_trajins()
    parmtop = "m1.prmtop"
    restricted_atoms = None
    if should_update_nmr(traj_data):
        restricted_atoms = get_list_restricted_atoms(traj_data, parmtop, trajins, closest_outputs)
        distances = get_distances(traj_data, parmtop, trajins, closest_outputs, restricted_atoms[0].nresidues)
        NMRManager(traj_data.input_ceons, closest_outputs, restricted_atoms).update(distances, nmrdirs)
    dist_files = [toInputPath(create_dist_file_name(directory, traj))
                  for (directory, traj) in zip(nmrdirs, range(traj_data.number_trajectories))]
    NMRManager(traj_data.input_ceons, closest_outputs, restricted_atoms, dist_files).update_inputs()

def get_trajins(traj_data):
    return [restart_path(traj_data, traj, traj_data.user_input.restart_attempt)
            for traj in range(1, traj_data.number_trajectories+1)]

def restart_path(traj_data, trajectory, restart):
    return "{}/traj_{}/restart_{}/snap_for_{}_t{}_r{}.rst".format(traj_data.job_suffix,
                                                                  trajectory, restart,
                                                                  traj_data.job_suffix,
                                                                  trajectory, restart)

def should_update_nmr(traj_data):
    return (traj_data.user_input.restart_attempt == 0
            and traj_data.job_suffix == "qmground"
            and traj_data.user_input.restrain_solvents is True
            and traj_data.user_input.number_nearest_solvents > 0)

def get_list_restricted_atoms(traj_data, parmtop, trajins, closest_outputs):
    center_mask = traj_data.user_input.mask_for_center
    list_restricted_atoms = []
    for traj in range(traj_data.number_trajectories):
        print("Generating restricted atoms list for traj {}".format(traj+1))
        list_restricted_atoms.append(RestrictedAtoms(parmtop, trajins[traj], center_mask,
                                                     closest_outputs[traj]))
    return list_restricted_atoms
