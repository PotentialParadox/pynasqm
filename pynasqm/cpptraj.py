'''
Functions for nasqm that interface with cpptraj
'''
import subprocess
import re
import numpy as np

def create_restarts(amber_inputfile, output, step=None):
    '''
    Create amber restart files using cpptraj
    '''
    ctc = 'parm m1.prmtop\n'
    if step is not None:
        ctc += "trajin {} 1 last {}\n".format(amber_inputfile, step)
    else:
        ctc += "trajin {} 1 last\n".format(amber_inputfile)
    ctc += 'center :1\n' \
           'trajout {} restart\n' \
           'image\n' \
           'run\n' \
           'quit'.format(output)
    open('convert_to_crd.in', 'w').write(ctc)
    print("Creating restarts from", amber_inputfile)
    subprocess.run(['cpptraj', '-i', 'convert_to_crd.in', '-o', 'convert_to_crd.out'])


