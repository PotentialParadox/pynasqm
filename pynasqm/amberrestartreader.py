class AmberRestartReader:
    def __init__(self, filename):
        self._filestring = open(filename, 'r').read()
        self._number_atoms = self._getnatoms()
        self.header = self._readheader()
        self.coordinates = self._readcoords()
        self.velocities =self._readvelocs()

    def _getnatoms(self):
        toplines = self._filestring.split('\n')[0:2]
        options = toplines[1].split()
        return int(options[0])

    def _readheader(self):
        toplines = self._filestring.split('\n')[0:2]
        return "{}\n{}\n".format(toplines[0], toplines[1])

    def _readcoords(self):
        lines = self._filestring.split('\n')
        residue = self._number_atoms % 2
        end_line = int(self._number_atoms / 2 + residue + 2)
        coordinates = []
        for line in range(2, end_line):
            coords = [float(x) for x in lines[line].split()]
            if len(coords) > 3:
                coordinates.append([coords[0], coords[1], coords[2]])
                coordinates.append([coords[3], coords[4], coords[5]])
            else:
                coordinates.append([coords[0], coords[1], coords[2]])
        return coordinates

    def _readvelocs(self):
        lines = self._filestring.split('\n')
        residue = self._number_atoms % 2
        start_line = int(self._number_atoms / 2 + residue + 2)
        end_line = int(start_line*2 - 2)
        velocities = []
        for line in range(start_line, end_line):
            velocs = [float(x) for x in lines[line].split()]
            if len(velocs) > 3:
                velocities.append([velocs[0], velocs[1], velocs[2]])
                velocities.append([velocs[3], velocs[4], velocs[5]])
            else:
                velocities.append([velocs[0], velocs[1], velocs[2]])
        return velocities
