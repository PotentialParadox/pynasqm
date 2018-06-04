import re

def get_fortran_nml(filename, nml):
    '''
    Returns a string of the block between the namelist labels
    '''
    p_start = re.compile(r"\&{}".format(nml))
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
