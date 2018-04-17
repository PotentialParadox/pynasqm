from pynasqm.maskreader import MaskReader
from pynasqm.residueconverter import ResidueConverter
from pynasqm.closestreader import ClosestReader

class RestrictedAtomRetriever:

    def __init__(self, parmtop, trajins, mask, closest_out):
        self._parmtop = parmtop
        self._trajins = trajins
        self._mask = mask
        self._closest_output = closest_out
        self.solvent_atoms = self._get_restricted_solvent_atoms()
        self.solute_atoms = self._get_restricted_solute_atoms()

    def get_restricted_list(self):
        '''
        | 1st set restricted atoms of solute | 1st set restricted atoms of solutions |
        | 2nd set restricted atoms of solute | 2nd set restricted atoms of solutions |
        '''
        solute_atoms = self._get_restricted_solute_atoms()
        return solute_atoms

    def _get_restricted_solute_atoms(self):
        mask = self._mask
        mask_reader = MaskReader(mask)
        atoms_or_residues = mask_reader.get_list()
        atoms = None
        if (mask_reader.type() == 'residue' and len(atoms_or_residues) > 1):
            raise ValueError("Mask of center should only be 1 residue or a collection of atoms")
        if mask_reader.type() == 'residue':
            atoms = ResidueConverter(self._parmtop, self._trajins[0]).residue_to_atoms(atoms_or_residues[0])
        if mask_reader.type() == 'atom':
            atoms = atoms_or_residues
        return atoms * len(self.solvent_atoms)

    def _get_restricted_solvent_atoms(self):
        reader = ClosestReader(self._closest_output)
        residues = reader.residues
        atom_list = []
        for residue in residues:
            atoms = ResidueConverter(self._parmtop, self._trajins[0]).residue_to_atoms(residue)
            atom_list.append(atoms)
        return atom_list


