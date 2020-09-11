'''
Functions for nasqm that interface with cpptraj
'''
import os
from pynasqm.utils import copy_file
import subprocess

def create_restarts(amber_inputfile, output, start=1, last="last", step=None, override=None, center=True):
    '''
    Create amber restart files using cpptraj
    '''
    if os.path.isfile(amber_inputfile):
        ctc = 'parm m1.prmtop\n'
        if step is not None:
            ctc += f"trajin {amber_inputfile} {start} {last} {step}\n"
        else:
            ctc += f"trajin {amber_inputfile}\n"
        if center:
            ctc += "center :1\n"
        ctc += f"trajout {output} restart\n"
        if center:
            ctc += f"image\n"
        ctc += f"run\n" \
            f"quit"
        open('convert_to_crd.in', 'w').write(ctc)
        print("Creating restarts from", amber_inputfile)
        subprocess.run(['cpptraj', '-i', 'convert_to_crd.in', '-o', 'convert_to_crd.out'])
    else:
        copy_file(amber_inputfile, output)
