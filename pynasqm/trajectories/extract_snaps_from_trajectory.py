'''
Functions for nasqm that interface with cpptraj
'''
import os
from pynasqm.utils import copy_file
import subprocess

def extract_snaps_from_trajectory(trajectory_files, output, start=1, last="last", step=None, override=None, center=True):
    '''
    Create amber restart files using cpptraj
    '''
    ctc = 'parm m1.prmtop\n'
    for traj in trajectory_files:
        if step is not None:
            ctc += f"trajin {traj} {start} {last} {step}\n"
        else:
            ctc += f"trajin {traj}\n"
    if center:
        ctc += "center :1\n"
    ctc += f"trajout {output} restart\n"
    if center:
        ctc += f"image\n"
    ctc += "run\n" \
        "quit"
    open('convert_to_crd.in', 'w').write(ctc)
    print("Creating restarts from", trajectory_files)
    subprocess.run(['cpptraj', '-i', 'convert_to_crd.in', '-o', 'convert_to_crd.out'])
