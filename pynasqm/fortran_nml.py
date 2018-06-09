import re

class FortranNml:

    def __init__(self, nml):
        self._nml = nml
        self._nml_data = [] #[(label, values)]

    def get_fortran_nml(self, filename):
        block_string = self.get_block_string(filename)
        self._nml_data = self.block_to_data(block_string)

    def get_block_string(self, filename):
        '''
        IO -> [String]
        Returns a list of line string of the block between the namelist labels
        '''
        p_start = re.compile(r"\&{}".format(self._nml))
        p_end = re.compile(r"\&end")
        nml_block = []
        with open(filename, 'r') as fin:
            for lines in fin:
                if re.search(p_start, lines):
                    for lines2 in fin:
                        if re.search(p_end, lines2):
                            break
                        nml_block.append(lines2)
        return nml_block

    def block_to_data(self, block_string):
        '''
        [String] -> [(label, values)]
        '''
        return [self.split_line_string(x) for x in block_string]

    def split_line_string(self, line_string):
        '''
        String -> (label, value)
        '''
        commaless = self.remove_last_comma(line_string)
        split = commaless.split('=')
        return (split[0], split[1])

    def data_to_string(self):
        '''
        [(label, values)] -> String
        '''
        lines = ["  {}={}\n".format(x[0], x[1]) for x in self._nml_data]
        return ''.join(lines)

    def __str__(self):
        '''
        FortranNml -> String
        '''
        output = "&{}\n".format(self._nml)
        output += self.data_to_string()
        output += "&end{}\n".format(self._nml)

    @staticmethod
    def remove_last_comma(line_string):
        '''
        String -> String
        '''
        if line_string[-1] == ',':
            return line_string[:-1]
        return line_string
