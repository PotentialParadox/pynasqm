from pynasqm.nmr.get_nmrdirs import get_nmrdirs
from pynasqm.nmr.closestreader import ClosestReader
from pynasqm.nmr.trajdistance import TrajDistance

def get_distances(traj_data, parmtop, trajins, closest_outputs, nresidues):
    center_mask = traj_data.user_input.mask_for_center
    added_buffer = 0.0
    list_distances = []
    for traj, nmrdir in zip(range(traj_data.number_trajectories), get_nmrdirs(traj_data)):
        residues = [":{}".format(x) for x in ClosestReader(closest_outputs[traj]).residues]
        trajdist = TrajDistance(parmtop, center_mask)
        distances = [trajdist(trajins[traj], residue, traj, nmrdir) + added_buffer for residue in residues]
        maxdistance = max(distances)
        newdistances = [maxdistance for _ in distances]
        distances = newdistances
        far_distances = [-maxdistance for _ in range(nresidues-len(distances)-1)]
        distances = distances + far_distances
        list_distances.append(distances)
    return list_distances
