'''
Unit Tests for nasqm_write
'''
import os
import pynasqm.write as nasqm_write
import numpy as np
import pytest
import subprocess

def setup_module(module):
    '''
    Switch to test directory
    '''
    os.chdir("tests/nasqmWrite")

def teardown_module(module):
    '''
    Return to main directory
    '''
    os.chdir("../..")

# def test_strip_timedelay():
#     '''
#     Test to see if the timedelay strip routine removes the
#     approriate data
#     '''
#     test_string = open("spectra_flu.input").read()
#     results = nasqm_write.strip_timedelay(test_string, 2, 0.5, 2)
#     print(results)
#     assert results == '    2.70677444298323E+00    1.00507770698760E+00\n'\
#                       '    2.50629011440210E+00    1.06776301983101E+00\n'

# def test_truncate_spectra():
#     '''
#     Test to see if truncate spectra removes the appropriate
#     data
#     '''
#     test_string = open("spectra_flu.input").read()
#     results = nasqm_write.truncate_spectra(test_string, 2, 0.5, 2)
#     assert results == '    2.76321917652115E+00    9.81624195302620E-01\n'\
#                       '    2.67137127196091E+00    1.01733845823091E+00\n'

# def test_strip_timedelay_exception():
#     '''
#     Test to see if exception is thown if timedelay is too large
#     '''
#     test_string = open("spectra_flu.input").read()
#     with pytest.raises(Exception):
#         nasqm_write.strip_timedelay(test_string, 2, 0.5, 20)


# def test_numpy_to_spectra_string():
#     '''
#     Tests whether numpy to string converts properly using data from the
#     previous test
#     '''
#     data = np.array([[2.90923255131416, 9.08120295476811E-01],
#                      [2.90923255131440, 9.08120295476795E-01]])
#     results = nasqm_write.numpy_to_specta_string(data)
#     assert results == '    2.90923255131416E+00    9.08120295476811E-01\n'\
#                       '    2.90923255131440E+00    9.08120295476795E-01\n'

def test_accumulate_spectra():
    '''
    Test reading from one trajectory and one state for 0 restarts
    '''
    results, _ = nasqm_write.accumulate_spectra(n_trajectories=1, n_states=1, suffix='abs')
    print(results)
    assert results == '    2.81546056752562E+00    1.08396426502947E+00\n'\
                      '    2.81546056803794E+00    1.08396426443482E+00\n'\
                      '    2.82143633193210E+00    1.07674514101601E+00\n'\

def test_accumulate_spectra1r():
    '''
    Test reading from one trajectory and one state for 1 restart
    '''
    results, _ = nasqm_write.accumulate_spectra(n_trajectories=1, n_states=1, suffix='abs', n_restarts=1)
    print(results)
    assert results == '    2.81546056752562E+00    1.08396426502947E+00\n'\
                      '    2.81546056803794E+00    1.08396426443482E+00\n'\
                      '    2.82143633193210E+00    1.07674514101601E+00\n'\
                      '    2.83499537579971E+00    1.09712749914004E+00\n'\
                      '    2.83499537590646E+00    1.09712749898366E+00\n'\
                      '    2.84494863011054E+00    1.09014408841436E+00\n'\

def test_accumulate_spectra2s():
    '''
    Test reading from one trajectory and two states for 0 restarts
    Format line = omega1 dipole1 omega2 dipole2
    '''
    results, _ = nasqm_write.accumulate_spectra(n_trajectories=1, n_states=2, suffix='abs', n_restarts=0)
    print(results)
    assert results == '    2.81546056752562E+00    1.08396426502947E+00    3.11283401561629E+00    1.71114020911819E-03\n'\
                      '    2.81546056803794E+00    1.08396426443482E+00    3.11283401572716E+00    1.71114021120587E-03\n'\
                      '    2.82143633193210E+00    1.07674514101601E+00    3.13879515381299E+00    1.40558935033439E-03\n'\

def test_accumulate_spectra2t():
    '''
    Test reading from two trajectories and one state for 0 restarts
    '''
    results, _ = nasqm_write.accumulate_spectra(n_trajectories=2, n_states=1, suffix='abs', n_restarts=0)
    print(results)
    assert results == '    2.81546056752562E+00    1.08396426502947E+00\n'\
                      '    2.81546056803794E+00    1.08396426443482E+00\n'\
                      '    2.82143633193210E+00    1.07674514101601E+00\n'\
                      '    2.79251675025885E+00    9.97596401377230E-01\n'\
                      '    2.79251675255889E+00    9.97596395053960E-01\n'\
                      '    2.77394015210517E+00    1.02463291276291E+00\n'\

def test_accumulate_spectra3t2rf():
    '''
    Test discarding a failed job that completes the zeroth restart but not the first restart
    '''
    results, _ = nasqm_write.accumulate_spectra(n_trajectories=3, n_states=1, suffix='abs', n_restarts=1)
    print(results)
    assert results == '    2.81546056752562E+00    1.08396426502947E+00\n'\
                      '    2.81546056803794E+00    1.08396426443482E+00\n'\
                      '    2.82143633193210E+00    1.07674514101601E+00\n'\
                      '    2.83499537579971E+00    1.09712749914004E+00\n'\
                      '    2.83499537590646E+00    1.09712749898366E+00\n'\
                      '    2.84494863011054E+00    1.09014408841436E+00\n'\
                      '    2.79251675025885E+00    9.97596401377230E-01\n'\
                      '    2.79251675255889E+00    9.97596395053960E-01\n'\
                      '    2.77394015210517E+00    1.02463291276291E+00\n'\
                      '    2.76745094266644E+00    1.08681417088910E+00\n'\
                      '    2.76745094348021E+00    1.08681416841911E+00\n'\
                      '    2.75412095067397E+00    1.11226755671165E+00\n'\

def test_as_missing_file():
    '''
    For accumulate spectra, make sure it can discard trajectories that don't start all their restarts
    '''
    results, _ = nasqm_write.accumulate_spectra(n_trajectories=4, n_states=1, suffix='abs', n_restarts=1)
    print(results)
    assert results == '    2.81546056752562E+00    1.08396426502947E+00\n'\
                      '    2.81546056803794E+00    1.08396426443482E+00\n'\
                      '    2.82143633193210E+00    1.07674514101601E+00\n'\
                      '    2.83499537579971E+00    1.09712749914004E+00\n'\
                      '    2.83499537590646E+00    1.09712749898366E+00\n'\
                      '    2.84494863011054E+00    1.09014408841436E+00\n'\
                      '    2.79251675025885E+00    9.97596401377230E-01\n'\
                      '    2.79251675255889E+00    9.97596395053960E-01\n'\
                      '    2.77394015210517E+00    1.02463291276291E+00\n'\
                      '    2.76745094266644E+00    1.08681417088910E+00\n'\
                      '    2.76745094348021E+00    1.08681416841911E+00\n'\
                      '    2.75412095067397E+00    1.11226755671165E+00\n'\

