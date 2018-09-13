import subprocess

class ResidueConverter:

    def __init__(self, parmtop, trajin):
        self._parmtop = parmtop
        self._trajin = trajin
        self._scriptfile = "atominfo.in"
        self._outputfile = "atominfo.out"

    def residue_to_atoms(self, residue):
        mask = self._create_resmask(residue)
        script = self._create_scriptfile(mask)
        self._write_script(script)
        self._run()
        answer = self._extract_atoms()
        return answer

    def _extract_atoms(self):
        with open(self._outputfile, 'r') as atominfo_stream:
            lines = atominfo_stream.readlines()[1:]
            atoms = []
            for line in lines:
                atoms.append(int(line.split()[0]))
            return atoms

    def _run(self):
        subprocess.Popen(['cpptraj', '-i', self._scriptfile, '-o', 'atominfo.log'], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

    def _create_scriptfile(self, mask):
        scriptstring = "parm {}\n".format(self._parmtop)
        scriptstring += "trajin {}\n".format(self._trajin)
        scriptstring += "atominfo {} out {}\n".format(mask, self._outputfile)
        scriptstring += "run\n"
        scriptstring += "exit\n"
        return scriptstring

    def _write_script(self, script):
        open(self._scriptfile, 'w').write(script)

    @staticmethod
    def _create_resmask(residue):
        if isinstance(residue, str):
            return residue
        return ":{}".format(residue)
