from pynasqm.maskreader import MaskReader
from pynasqm.residueconverter import ResidueConverter
from pynasqm.closestreader import ClosestReader

class RestrictedAtoms:

    def __init__(self, parmtop, trajin, mask, closest_out):
        self._parmtop = parmtop
        self._trajin = trajin
        self._mask = mask
        self._closest_output = closest_out
        self.solvent_atoms = self._get_restricted_solvent_atoms()
        self.solute_atoms = self._get_restricted_solute_atoms()

    def _get_restricted_solute_atoms(self):
        mask = self._mask
        mask_reader = MaskReader(mask)
        atoms_or_residues = mask_reader.get_list()
        atoms = None
        if (mask_reader.type() == 'residue' and len(atoms_or_residues) > 1):
            raise ValueError("Mask of center should only be 1 residue or a collection of atoms")
        if mask_reader.type() == 'residue':
            atoms = ResidueConverter(self._parmtop, self._trajin).residue_to_atoms(atoms_or_residues[0])
        if mask_reader.type() == 'atom':
            atoms = atoms_or_residues
        list_atoms = []
        for _ in range(self._number_solvent_residues()):
            list_atoms.append(atoms)
        return list_atoms

    def _number_solvent_residues(self):
        return len(self.solvent_atoms)

    def _get_restricted_solvent_atoms(self):
        reader = ClosestReader(self._closest_output)
        residues = reader.residues
        atom_list = []
        for residue in residues:
            atoms = ResidueConverter(self._parmtop, self._trajin).residue_to_atoms(residue)
            atom_list.append(atoms)
        return atom_list


