'''
Units tests for the cpptraj wrappers for nasqm
'''
import os
import pytest
import numpy as np
from pynasqm.inputceonwriter import InputceonWriter

def setup_module(module):
    '''
    Switch to test directory
    '''
    os.chdir("tests")

def teardown_module(module):
    '''
    Return to main directory
    '''
    os.chdir("..")

def test_writerestart():
    result_file = "inputceonwriter_result.txt"
    answer_file = "inputceonwriter_test.txt"
    header = "&qmmm\n"\
             "  qm_theory='AM1',\n"\
             "  scfconv=1.0000E-16,\n"\
             "&endqmmm\n\n"\
             "&moldyn\n"\
             "   out_data_cube=0, ! write(1) or not(0) view files to generate cubes [0]\n"\
             "   out_count_init=0, ! the initial count for output files [0]\n"\
             "&endmoldyn\n"
    coords = [[6, 33.0705422083, 29.9883909408, 28.8406162421],
              [8, 30.8615530208, 29.3467664264, 30.5453436989],
              [1, 33.7970847279, 29.5510275220, 28.1006645527]]
    velocities = [[-10.1549436002, -6.0082457442, 4.2490486703],
                  [-4.1236544153, 24.4998942617, -9.7412784148],
                  [ 3.0327485256, -9.9224458080, 6.2971860132]]
    coeff = [[0.0000000000, 0.8057219375],
             [1.0000000000, 0.3582782236],
             [0.0000000000, 0.4546264694]]
    writer = InputceonWriter(header, coords, velocities, coeff)
    writer.write(result_file)
    result = open(result_file, 'r').read()
    answer = open(answer_file, 'r').read()
    assert result == answer
