'''
Units tests for the cpptraj wrappers for nasqm
'''
import os
import pytest
import numpy as np
from pynasqm.residueconverter import ResidueConverter

def setup_module(module):
    '''
    Switch to test directory
    '''
    os.chdir("tests/residueConverter")

def teardown_module(module):
    '''
    Return to main directory
    '''
    os.chdir("../..")

def test_residue_converter():
    parmtop = "m1.prmtop"
    trajin = "ground_snap.1"
    residue = 2
    rconverter = ResidueConverter(parmtop, trajin)
    result = rconverter.residue_to_atoms(residue)
    assert result == [51, 52, 53, 54, 55]
