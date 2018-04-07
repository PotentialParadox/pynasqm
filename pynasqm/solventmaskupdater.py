import subprocess
from pynasqm.closestwriter import ClosestWriter
from pynasqm.closestreader import ClosestReader

class SolventMaskUpdater:

    def __init__(self, input_ceons, user_input):
        self._input_ceons = input_ceons
        self._user_input = user_input
        self._trajins = self._default_trajins()
        self._masks = None

    def update_masks(self):
        outputs = self._create_closest_outputs()
        self._create_masks(outputs)
        self._set_masks_in_input()

    def _default_trajins(self):
        trajins = []
        for i in range(1, self._number_trajectories()+1):
            trajins.append("ground_snap.{}".format(i))
        return trajins

    def _create_masks(self, outputs):
        masks = []
        for output in outputs:
            reader = ClosestReader(output)
            residues = reader.residues
            masks.append(self._convert_residues_to_mask(residues))
        self._masks = masks

    @staticmethod
    def _convert_residues_to_mask(residues):
        mask = "':1"
        for residue in residues:
            mask += ",{0:.0f}".format(residue)
        mask += "'"
        return mask

    def _create_closest_outputs(self):
        number_solvents = self._user_input.number_nearest_solvents
        writer = ClosestWriter(self._trajins, number_solvents)
        writer.write()
        self._run_closest_scripts(writer.script_files)
        return writer.trajouts

    @staticmethod
    def _run_closest_scripts(file_names):
        for script in file_names:
            subprocess.call(['cpptraj', '-i', script, '-o', 'cpptraj.out'])

    def _number_nearest_solvents(self):
        return self._user_input.number_nearest_solvents

    def _number_trajectories(self):
        return len(self._input_ceons)

    def _set_masks_in_input(self):
        number_trajectories = self._number_trajectories()
        for trajectory in range(number_trajectories):
            mask = self._masks[trajectory]
            self._input_ceons[trajectory].set_mask(mask)
