from pynasqm.closestreader import ClosestReader
from pynasqm.closestrunner import ClosestRunner

class SolventMaskUpdater:

    def __init__(self, input_ceons, user_input, outputs):
        self._input_ceons = input_ceons
        self._user_input = user_input
        self._outputs = outputs
        self._trajins = self._default_trajins()
        self._masks = None

    def update_masks(self):
        self._create_masks(self._outputs)
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


    def _number_nearest_solvents(self):
        return self._user_input.number_nearest_solvents

    def _number_trajectories(self):
        return len(self._input_ceons)

    def _set_masks_in_input(self):
        number_trajectories = self._number_trajectories()
        for trajectory in range(number_trajectories):
            mask = self._masks[trajectory]
            self._input_ceons[trajectory].set_mask(mask)
