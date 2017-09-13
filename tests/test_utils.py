'''
Unit tests for pynasqm.utils functions
'''
import os
import pynasqm.utils
import numpy as np

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

def test_numpy_to_txt_1():
    '''
    Test whether a single row of integers will print correctly
    '''
    test = np.array([1, 2, 3])
    result = pynasqm.utils.numpy_to_txt(test)
    assert result == " 1 2 3 "

def test_numpy_to_txt_1f():
    '''
    Test whether a single row of floats will print correctly
    '''
    test = np.array([1.1, 2.2, 3.3])
    result = pynasqm.utils.numpy_to_txt(test)
    assert result == "  1.1  2.2  3.3 "

def test_numpy_to_txt_2f():
    '''
    Test whether a single row of floats will print correctly
    '''
    test = np.array([[1.1, 2.2, 3.3], [4.4, 5.5, 6.6]])
    result = pynasqm.utils.numpy_to_txt(test)
    assert result == "   1.1  2.2  3.3 \n" \
                     "   4.4  5.5  6.6  "
