'''
Units tests for the cpptraj wrappers for nasqm
'''
import os
import pytest
import numpy as np
from pynasqm.closestwriter import ClosestWriter
import pynasqm.userinput as nasqm_user_input
import pynasqm.inputceon as inputceon

def setup_module(module):
    '''
    Switch to test directory
    '''
    os.chdir("tests/closestWriter")

def teardown_module(module):
    '''
    Return to main directory
    '''
    os.chdir("../..")

def test_write_closest_traj():
    trajin = "ground_snap.1"
    number_nearest = 3
    closests = ClosestWriter(trajin, number_nearest)
    closests.write()
    result = open("1/closest_1.traj", 'r').read()
    answer = open("closest_1_test.traj", 'r').read()
    assert result == answer

def test_write_closest_traj2():
    trajin = ["ground_snap.1", "ground_snap.2"]
    number_nearest = 3
    closests = ClosestWriter(trajin, number_nearest)
    closests.write()
    result = open("2/closest_2.traj", 'r').read()
    answer = open("closest_2_test.traj", 'r').read()
    assert result == answer
