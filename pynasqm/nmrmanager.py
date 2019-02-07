import re
from pynasqm.closestreader import ClosestReader
from pynasqm.nmrwriterfactory import NMRWriterFactory
from pynasqm.maskreader import MaskReader
from pynasqm.residueconverter import ResidueConverter

class NMRManager:

    def __init__(self, input_ceons, closest_outputs, restricted_atoms, distances, dist_files=[]):
        self._input_ceons = input_ceons
        self._closest_outputs = closest_outputs
        self._number_trajectories = self._get_number_trajectories()
        self._restricted_atoms = restricted_atoms
        self._distances = distances
        self._dist_files = dist_files

    def update(self, nmr_directories=None):
        self.write_dist_files(nmr_directories)
        self.update_inputs()

    def write_dist_files(self, nmr_directories=None):
        if nmr_directories is None:
            nmr_directories = ["{}".format(i) for i in range(1, self._get_number_trajectories())]
        for trajectory, directory in zip(range(self._get_number_trajectories()), nmr_directories):
            restricted_atoms1 = self._restricted_atoms[trajectory].solute_atoms
            restricted_atoms2 = self._restricted_atoms[trajectory].solvent_atoms
            desired_distances = self._distances[trajectory]
            for distance in desired_distances:
                if distance > 20:
                    raise ValueError("Desired distance {} for traj {} greater than 20, "\
                                     "possibly too many nearest solvent".format(distance,
                                                                                trajectory+1))
            file_name = self._create_dist_file_name(directory, trajectory)
            self._dist_files.append(self.toInputPath(file_name))
            nmrfactory = NMRWriterFactory(restricted_atoms1, restricted_atoms2, desired_distances)
            nmrwriter = nmrfactory.get_writer()
            nmrwriter.write_to(file_name)

    @staticmethod
    def toInputPath(filename):
        return "../nmr/{}".format((filename.split('/'))[-1])

    def update_inputs(self):
        for trajectory in range(self._number_trajectories):
            self._input_ceons[trajectory].set_nmr_directory(self._dist_files[trajectory])

    @staticmethod
    def _create_dist_file_name(directory, index):
        return "{}/rst_{}.dist".format(directory, index+1)


    def _get_number_trajectories(self):
        n_trajs = len(self._input_ceons)
        if len(self._closest_outputs) != n_trajs:
            raise AttributeError("number of input_ceon must equal number of" \
                                 "closest outputs")
        return n_trajs
