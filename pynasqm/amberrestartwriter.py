class AmberRestartWriter:
    def __init__(self, header, coordinates, velocities):
        self._header = header
        self._coordinates = coordinates
        self._velocities = velocities

    def write(self, filename):
        coordinate_string = ""
        velocity_string = ""
        coordinate_string = self._array_string(self._coordinates, coordinate_string)
        velocity_string = self._array_string(self._velocities, velocity_string)
        file_string = "{}{}{}".format(self._header, coordinate_string, velocity_string)
        open(filename, 'w').write(file_string)

    def _array_string(self, array, array_string):
        if len(array) == 1:
            for i in range(3):
                array_string += "{:12.7f}".format(array[0][i])
            array_string += "\n"
            return array_string
        if len(array) == 2:
            for i in range(3):
                array_string += "{:12.7f}".format(array[0][i])
            for i in range(3):
                array_string += "{:12.7f}".format(array[1][i])
            array_string += "\n"
            return array_string
        if len(array) > 2:
            for i in range(3):
                array_string += "{:12.7f}".format(array[0][i])
            for i in range(3):
                array_string += "{:12.7f}".format(array[1][i])
            array_string += "\n"
            array_string = self._array_string(array[2:], array_string)
            return array_string



