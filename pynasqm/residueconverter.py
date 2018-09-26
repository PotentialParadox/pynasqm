import subprocess

class ResidueConverter:

    def __init__(self, parmtop, trajin):
        self._parmtop = parmtop
        self._trajin = trajin
        self._scriptfile = "atominfo.in"
        self._outputfile = "atominfo.out"
        self._atomlists = None

    def residue_to_atoms(self, residue):
        if self._atomlists is None:
            self._atomlists = self.gen_atomlists()
        if residue > len(self._atomlists):
            raise ValueError("residue to convert must exist")
        return self._atomlists[residue-1]

    def gen_atomlists(self):
        return self.atomresidue_to_atomlists(self.parse_atomresidue(self.atominfo()))

    @staticmethod
    def atomresidue_to_atomlists(atomresidue):
        '''
        [[atom, residue]] -> [residue,[atom]]
        '''
        current_residue = 1
        atomlists = []
        current_list = []
        for line in atomresidue:
            if line[1] != current_residue:
                atomlists.append(current_list)
                current_residue += 1
                current_list = []
            current_list.append(line[0])
        atomlists.append(current_list)
        return atomlists

    @staticmethod
    def parse_atomresidue(atominfo):
        '''
        string -> [[atom, residue]]
        '''
        lines = atominfo.split('\n')
        data = [x.split() for x in lines[1:-1]]
        return [[int(x[0]),int(x[2])] for x in data]


    def atominfo(self):
        script = self._create_scriptfile()
        self._write_script(script)
        self._run(script)
        return open(self._outputfile, 'r').read()

    def extract_atoms(self):
        with open(self._outputfile, 'r') as atominfo_stream:
            lines = atominfo_stream.readlines()[1:]
            atoms = []
            for line in lines:
                atoms.append(int(line.split()[0]))
            return atoms

    @staticmethod
    def _run(script):
        p1 = subprocess.Popen(['echo', script], stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
        p2 = subprocess.Popen(['cpptraj'], stdin=p1.stdout,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p1.stdout.close()
        stdout = p2.communicate()[0]

    def _create_scriptfile(self):
        scriptstring = "parm {}\n".format(self._parmtop)
        scriptstring += "trajin {}\n".format(self._trajin)
        scriptstring += "atominfo :* out {}\n".format(self._outputfile)
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
