import re

class FortranNml:

    def __init__(self, nml):
        self._nml = nml
        self._nml_data = None

    def get_fortran_nml(self, filename):
        block_string = self.get_block_string(filename)
        self._nml_data = self.block_to_data(block_string)

    def get_block_string(self, filename):
        '''
        IO -> [String]
        Returns a list of line string of the block between the namelist labels
        '''
        p_start = re.compile(r"^\s*\&{}".format(self._nml))
        p_end = re.compile(r"(^\s*\&end|^\s*\/)")
        nml_block = []
        with open(filename, 'r') as fin:
            for lines in fin:
                if re.search(p_start, lines):
                    for lines2 in fin:
                        if re.search(p_end, lines2):
                            m = re.findall(p_end, lines2)
                            break
                        nml_block.append(lines2)
        return nml_block

    @staticmethod
    def is_comment(s):
        '''
        String -> Bool
        '''
        for x in s:
            if x != ' ' and x != '!' and x !='\t' and x != '\n':
                return False
            if x == '!' or x == '\n':
                return True
        return True

    def remove_comment(self, s):
        '''
        String -> String
        '''
        value = s
        if '!' in s:
            [value, _] = s.split('!')
        splitvalues = value.split()
        return ''.join(splitvalues)

    def block_to_data(self, block_string):
        '''
        [String] -> {label, values}
        '''
        data_dictionary = dict()
        for x in block_string:
            if not self.is_comment(x):
                (key, value) = self.split_line_string(x)
                data_dictionary[key] = value
        return data_dictionary

    def split_line_string(self, line_string):
        '''
        String -> (label, value)
        '''
        commentless = self.remove_comment(line_string)
        commaless = self.remove_last_comma(commentless)
        split = commaless.split('=')
        return (split[0], split[1])

    def data_to_string(self):
        '''
        [(label, values)] -> String
        '''
        lines = ["  {}={},\n".format(key, self._nml_data[key]) for key in self._nml_data]
        return ''.join(lines)

    def __str__(self):
        '''
        FortranNml -> String
        '''
        output = "&{}\n".format(self._nml)
        output += self.data_to_string()
        output += "&end{}\n".format(self._nml)
        return output

    def set_value(self, key, value):
        self._nml_data[key] = value

    @staticmethod
    def remove_last_comma(line_string):
        '''
        String -> String
        '''
        if line_string[-1] == ',':
            return line_string[:-1]
        return line_string
