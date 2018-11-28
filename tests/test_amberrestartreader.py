'''
Units tests for the cpptraj wrappers for nasqm
'''
import os
import pytest
import numpy as np
from pynasqm.amberrestartreader import AmberRestartReader

def setup_module(module):
    '''
    Switch to test directory
    '''
    os.chdir("tests/amberRestartReader")

def teardown_module(module):
    '''
    Return to main directory
    '''
    os.chdir("../..")

def test_readheader():
    restart_file = "amberrestartwriter_test.txt"
    header = "Cpptraj Generated Restart                                                       \n"\
             "   5  5.0500002E+00\n"
    reader = AmberRestartReader(restart_file)
    assert reader.header == header

def test_readcoordinates():
    restart_file = "amberrestartwriter_test.txt"
    coordinates = [[33.0501556, 30.0236702, 28.7626724],
                   [30.5973835, 29.6351776, 29.3849716],
                   [29.2811470, 29.6826267, 28.6972866],
                   [31.5950165, 29.9517136, 28.4902153],
                   [33.3797836, 29.3499241, 29.5741920]]
    reader = AmberRestartReader(restart_file)
    assert reader.coordinates == coordinates

def test_readvelocities():
    restart_file = "amberrestartwriter_test.txt"
    velocities = [[0.0512064, 0.0110960, 0.1382588],
                  [-0.1214809, -0.0143751, -0.0255557],
                  [0.0195328, 0.0069135, 0.0500221],
                  [0.0605416, 0.0443694, -0.0706517],
                  [-0.2138886, 0.3514622, -0.2833891]]
    reader = AmberRestartReader(restart_file)
    assert reader.velocities == velocities
