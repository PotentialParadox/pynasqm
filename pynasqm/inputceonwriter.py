class InputceonWriter:
    def __init__(self, header, coords, velocities, coeff):
        self._header = header
        self._coords = coords
        self._velocities = velocities
        self._coeff = coeff

    def write(self, filename):
        coord_string = self._coord_string()
        veloc_string = self._veloc_string()
        coeff_string = self._coeff_string()
        filestring = "{}\n{}\n{}\n{}\n".format(self._header, coord_string, veloc_string, coeff_string)
        open(filename, 'w').write(filestring)

    def _coord_string(self):
        coord_string = "&coord\n"
        for coord in self._coords:
            coord_string += "{:5d}{:12.7f}{:12.7f}{:12.7f}\n".format(coord[0], coord[1], coord[2], coord[3])
        coord_string += "&endcoord\n"
        return coord_string

    def _veloc_string(self):
        veloc_string = "&veloc\n"
        for veloc in self._velocities:
            veloc_string += "{:15.10f}{:15.10}{:15.10}\n".format(veloc[0], veloc[1], veloc[2])
        veloc_string += "&endveloc\n"
        return veloc_string

    def _coeff_string(self):
        coeff_string = "&coeff\n"
        for coeff in self._coeff:
            coeff_string += "{:15.12f}{:15.12}\n".format(coeff[0], coeff[1])
        coeff_string += "&endcoeff"
        return coeff_string
