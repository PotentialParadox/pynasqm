'''
Units tests for the cpptraj wrappers for nasqm
'''
import os
import pytest
import numpy as np
from pynasqm.trajdistance import TrajDistance

def setup_module(module):
    '''
    Switch to test directory
    '''
    os.chdir("tests/trajDistance")

def teardown_module(module):
    '''
    Return to main directory
    '''
    os.chdir("../..")

def test_trajdistance():
    parmtop = 'm1.prmtop'
    solute_mask = ':1'
    trajin = '1/ground_snap.1'
    solvent_mask = ':400'
    trajdist = TrajDistance(parmtop, solute_mask)
    distance = trajdist(trajin, solvent_mask)
    assert distance == 5.4782

def test_trajdistance2():
    parmtop = 'm1.prmtop'
    solute_mask = ':1'
    trajin = '2/ground_snap.2'
    solvent_mask = ':400'
    trajdist = TrajDistance(parmtop, solute_mask)
    distance = trajdist(trajin, solvent_mask, 1)
    assert distance == 5.8772
