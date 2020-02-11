'''
Functions for nasqm that interface with cpptraj
'''
import os
from pynasqm.utils import copy_file
import subprocess

def create_restarts(amber_inputfile, output, step=None, override=None):
    '''
    Create amber restart files using cpptraj
    '''
    if os.path.isfile(amber_inputfile):
        ctc = 'parm m1.prmtop\n'
        if step is not None:
            ctc += "trajin {} 1 last {}\n".format(amber_inputfile, step)
        else:
            ctc += "trajin {}\n".format(amber_inputfile)
        ctc += 'center :1\n' \
            'trajout {} restart\n' \
            'image\n' \
            'run\n' \
            'quit'.format(output)
        open('convert_to_crd.in', 'w').write(ctc)
        print("Creating restarts from", amber_inputfile)
        subprocess.run(['cpptraj', '-i', 'convert_to_crd.in', '-o', 'convert_to_crd.out'])
    else:
        copy_file(amber_inputfile, output)
