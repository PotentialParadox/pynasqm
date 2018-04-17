'''
Units tests for the cpptraj wrappers for nasqm
'''
import os
import pytest
import numpy as np
from pynasqm.restrictedatoms import RestrictedAtoms

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

def test_get_restricted_list():
    parmtop = "m1.prmtop"
    trajin = 'ground_snap.1'
    mask = ':1'
    closest_out = 'closest_1.txt'
    retriever = RestrictedAtoms(parmtop, trajin, mask, closest_out)
    answer = []
    for _ in range(3):
        answer.append([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
                       12, 13, 14, 15, 16, 17, 18, 19, 20,
                       21, 22, 23, 24, 25, 26, 27, 28, 29,
                       30, 31, 32, 33, 34, 35, 36, 37, 38,
                       39, 40, 41, 42, 43, 44, 45, 46, 47,
                       48, 49, 50])
    assert retriever.solute_atoms == answer

def test_get_restricted_list1():
    parmtop = "m1.prmtop"
    trajin = 'ground_snap.1'
    mask = ':1'
    closest_out = 'closest_1.txt'
    retriever = RestrictedAtoms(parmtop, trajin, mask, closest_out)
    assert retriever.solvent_atoms == [[2041, 2042, 2043, 2044, 2045],
                                       [2321, 2322, 2323, 2324, 2325],
                                       [801, 802, 803, 804, 805]]
