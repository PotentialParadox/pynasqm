'''
Functions for nasqm that interface with cpptraj
'''
import subprocess
import re
import numpy as np

def create_restarts(amber_input, output, step=None):
    '''
    Create amber restart files using cpptraj
    '''
    ctc = 'parm m1.prmtop\n'
    if step is not None:
        ctc += "trajin {}.nc 1 last {}\n".format(amber_input, step)
    else:
        ctc += "trajin {}.nc 1 last\n".format(amber_input)
    ctc += 'center :1\n' \
           'trajout {} restart\n' \
           'image\n' \
           'run\n' \
           'quit'.format(output)
    open('convert_to_crd.in', 'w').write(ctc)
    subprocess.run(['cpptraj', '-i', 'convert_to_crd.in'])

def closest_script(user_input, snap_id):
    '''
    Creates a script to identify near solvents to later
    be included in the QM calculation
    '''
    nearest = user_input.number_nearest_solvents
    script = "parm m1.prmtop\n" \
             "solvent !:1\n" \
             "trajin ground_snap.{}\n" \
             "closest {} :1 closestout closest_{}.txt\n" \
             "run\n" \
             "quit\n".format(snap_id, nearest, snap_id)
    return script

def read_closest(input_stream):
    '''
    Read the residue ID's of the nearest solvents to
    the molecule of interest
    '''
    p_id = re.compile(r"\n\s+\d+\s+(\d+)\s+")
    closest_file = input_stream.read()
    search_results = re.findall(p_id, closest_file)
    id_array = [float(id_string) for id_string in search_results]
    return np.array(id_array)

def update_closest(user_input, input_ceon):
    '''
    Updates the masks to include the closest residues to the
    molecule of interest
    '''
    for i in range(1, len(input_ceon)+1):
        mask = ''
        if user_input.number_nearest_solvents is None:
            mask = "':1'"
        else:
            script = closest_script(user_input, i)
            script_file = "closest_{}.traj".format(i)
            open(script_file, 'w').write(script)
            subprocess.run(['cpptraj', '-i', script_file])
            closest_out = open("closest_{}.txt".format(i), 'r')
            ids = read_closest(closest_out)
            mask = "':1"
            for index in ids:
                mask += ",{0:.0f}".format(index)
            mask += "'"
        input_ceon[i-1].set_mask(mask)
