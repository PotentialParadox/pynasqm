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

def test_numpy_element():
    '''
    Test to see if a numpy array of shape [X,] returns the right number
    '''
    test = np.array([1, 2, 3])
    element_i = 1
    element_j = 1
    result = pynasqm.utils.numpy_element(test, element_i, element_j)
    assert result == 2

def test_numpy_element_1():
    '''
    Test to see if a numpy array of shape [X,N] returns the right number
    '''
    test = np.array([[1, 2, 3], [4, 5, 6]])
    element_i = 1
    element_j = 1
    result = pynasqm.utils.numpy_element(test, element_i, element_j)
    assert result == 5

def test_numpy_to_txt_1():
    '''
    Test whether a single row of integers will print correctly
    '''
    test = np.array([1, 2, 3])
    result = pynasqm.utils.numpy_to_txt(test)
    assert result == "       1       2       3"

def test_numpy_to_txt_1f():
    '''
    Test whether a single row of floats will print correctly
    '''
    test = np.array([1.1, 2.2, 3.3])
    result = pynasqm.utils.numpy_to_txt(test)
    assert result == "    1.1000    2.2000    3.3000"

def test_numpy_to_txt_2f():
    '''
    Test whether a single row of floats will print correctly
    '''
    test = np.array([[1.1, 2.2, 3.3], [4.4, 5.5, 6.6]])
    result = pynasqm.utils.numpy_to_txt(test)
    assert result == "    1.1000    2.2000    3.3000\n"\
                     "    4.4000    5.5000    6.6000\n"

test_numpy_to_txt_1()
