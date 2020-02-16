'''
Unit Tests for nasqm_write
'''
import os
import pynasqm.spectracollection as spectra_collect
import numpy as np
import pytest
import subprocess

def setup_module(module):
    '''
    Switch to test directory
    '''
    os.chdir("tests/spectraCollection")

def teardown_module(module):
    '''
    Return to main directory
    '''
    os.chdir("../..")

