'''
Units tests for the cpptraj wrappers for nasqm
'''
import os
import pytest
import numpy as np
from pynasqm.maskreader import MaskReader

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

def test_maskreader_type_a():
    mask = "@150"
    mask_type = MaskReader(mask).type()
    assert mask_type == "atom"

def test_maskreader_type_r():
    mask = ":150"
    mask_type = MaskReader(mask).type()
    assert mask_type == "residue"

def test_maskreader_type_e():
    mask = "*150"
    with pytest.raises(Exception):
        MaskReader(mask).type()

def test_maskreader_list():
    mask = ":150"
    result = MaskReader(mask).get_list()
    assert result == [150]

def test_maskreader_list1():
    mask = ":150,162,178"
    result = MaskReader(mask).get_list()
    assert result == [150, 162, 178]

def test_maskreader_list2():
    mask = ":150-153"
    result = MaskReader(mask).get_list()
    assert result == [150, 151, 152, 153]

def test_maskreader_list3():
    mask = "@150-153, 160"
    result = MaskReader(mask).get_list()
    assert result == [150, 151, 152, 153, 160]
