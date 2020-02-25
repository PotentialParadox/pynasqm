'''
A unit tester for slurm.py
'''
import pytest
import os
from pynasqm.slurm import Slurm

def setup_module(module):
    '''
    Switch to test directory
    '''
    os.chdir("tests/slurm")

def teardown_module(module):
    '''
    Return to main directory
    '''
    os.chdir("../..")

SLURM_HEADER = {'email': "dtracy.uf@gmail.com", 'email_options': 3,
                'n_nodes': 1, 'ppn': 2, 'memory': "3000mb", 'walltime': "00:01:00",
                'max_jobs': 8, 'qos': 'roitberg'}

def test_email_options():
    '''
    test the email option
    '''
    slurm_object = Slurm(SLURM_HEADER)
    assert slurm_object.email_preferences == "BEGIN,END"

def test_create_slurm_script():
    '''
    Compare to a known working version of slurm
    '''
    command = 'echo "In this case SLURM_ARRAY_TASK_ID is $SLURM_ARRAY_TASK_ID" >>' \
              ' result_${SLURM_ARRAY_TASK_ID}.out\n'
    slurm_object = Slurm(SLURM_HEADER)
    job_script = slurm_object.create_slurm_script(command, "MyJob", "1-3")
    answer = str(open('slurm_test.txt', 'r').read())
    assert job_script == answer
