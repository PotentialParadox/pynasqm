'''
Units tests for the cpptraj wrappers for nasqm
'''
import os
import pytest
import numpy as np
from pynasqm.inputceonreader import InputceonReader

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

def test_read_coords():
    inputceon = "input_test.ceon"
    reader = InputceonReader(inputceon)
    result = reader.coords
    answer = [[6, 33.0705422083, 29.9883909408, 28.8406162421],
              [8, 30.8615530208, 29.3467664264, 30.5453436989],
              [1, 33.7970847279, 29.5510275220, 28.1006645527]]
    assert result == answer

def test_read_velocities():
    inputceon = "input_test.ceon"
    reader = InputceonReader(inputceon)
    result = reader.velocities
    answer = [[-10.1549436002, -6.0082457442, 4.2490486703],
              [-4.1236544153, 24.4998942617, -9.7412784148],
              [ 3.0327485256, -9.9224458080, 6.2971860132]]
    assert result == answer

def test_read_coeffs():
    inputceon = "input_test.ceon"
    reader = InputceonReader(inputceon)
    result = reader.coeffs
    answer = [[0.0000000000, 0.8057219375],
              [1.0000000000, 0.3582782236],
              [0.0000000000, 0.4546264694]]
    assert result == answer
