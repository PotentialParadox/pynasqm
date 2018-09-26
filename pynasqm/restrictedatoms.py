import re
import subprocess
from pynasqm.maskreader import MaskReader
from pynasqm.residueconverter import ResidueConverter
from pynasqm.closestreader import ClosestReader

class RestrictedAtoms:

    def __init__(self, parmtop, trajin, mask, closest_out):
        self._parmtop = parmtop
        self._trajin = trajin
        self._mask = mask
        self._closest_output = closest_out
        self.nresidues = self.get_number_residues()
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
        residues = ClosestReader(self._closest_output).residues
        solvents = self._convert_residues_to_atomgroups(residues)
        far_solvents = self._convert_residues_to_atomgroups(self.get_far_residues(residues))
        solvents = solvents + far_solvents
        return solvents

    def get_far_residues(self, close_solvents):
        return [x for x in range(2, self.nresidues+1) if x not in close_solvents]

    @staticmethod
    def get_number_residues():
        p1 = subprocess.Popen(['echo', 'parm m1.prmtop\n parminfo'], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        p2 = subprocess.Popen(['cpptraj'], stdin=p1.stdout, stdout=subprocess.PIPE)
        cout = p2.communicate()[0]
        cout = cout.decode()
        p_residue = re.compile(r"(\d+)\s+residues")
        residues = re.findall(p_residue, cout)
        return int(residues[0])

    def _convert_residues_to_atomgroups(self, residues):
        resconv = ResidueConverter(self._parmtop, self._trajin)
        return [resconv.residue_to_atoms(x) for x in residues]

