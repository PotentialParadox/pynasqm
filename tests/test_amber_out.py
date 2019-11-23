'''
Unit tests for amber_out
'''
import io
import os
import pytest
import pynasqm.amberout as amber_out
import numpy as np

def setup_module(module):
    '''
    Switch to test directory
    '''
    os.chdir("tests/amberOut")

def teardown_module(module):
    '''
    Return to main directory
    '''
    os.chdir("../..")


def test_find_excited_energies():
    '''
    Only tests the first state
    Test for multiple states exists in NexmdOutput
    '''
    test_string = "   1     2.72992400735139        -3.72988788959956       -0.503715618713691"\
                "0.101289783571188E-01     14.1658956897201\n"\
                "Total energy of the ground state (eV,AU)\n" \
                "0  -4012.58104634772       -147.459579686974\n"\
                "Total energies of excited states (eV,AU)\n"\
                "1  -4009.85112234037       -147.359256866811\n"\
                "QMMM:"

    output_stream = io.StringIO()
    test_file = "test_file"
    open(test_file, 'w').write(test_string)
    print("getting excited states")
    amber_out.find_excited_energies(test_file, output_stream, [1])
    output_string = output_stream.getvalue()
    output_stream.close()
    print(output_string)
    assert output_string == '   -4.00985112234037E+03\n'


def test_find_ground_energies():
    '''
    Only tests the first state
    Test for multiple states exists in NexmdOutput
    '''
    test_string = "   1     2.72992400735139        -3.72988788959956       -0.503715618713691"\
                "0.101289783571188E-01     14.1658956897201\n"\
                "Total energy of the ground state (eV,AU)\n" \
                "0  -4012.58104634772       -147.459579686974\n"\
                "Total energies of excited states (eV,AU)\n"\
                "1  -4009.85112234037       -147.359256866811\n"\
                "QMMM:"

    input_stream = io.StringIO(test_string)
    output_stream = io.StringIO()
    amber_out.find_ground_energies(input_stream, output_stream)
    output_string = output_stream.getvalue()
    output_stream.close()
    assert output_string == '   -4.01258104634772E+03\n'


def test_find_nasqm_excited_state_1():
    '''
    Tests to see if we can find the omega and total oscillator strength of 1st Excited states
    '''
    test_file = "nasqm_flu_1.out"
    result = amber_out.find_nasqm_excited_state(test_file)
    print(result)
    assert result == ""\
        "    2.90923223491635E+00    9.08434161983220E-01\n" \
        "    2.90923255131416E+00    9.08120295476811E-01\n" \
        "    2.90923255131440E+00    9.08120295476795E-01\n" \
        "    2.90576054156170E+00    9.12245042622513E-01\n" \
        "    2.89718863282344E+00    9.17508693665317E-01\n" \
        "    2.88542766911918E+00    9.23660450221756E-01\n"

def test_find_nasqm_excited_state_2():
    '''
    Tests to see if we can find the omega and total oscillator strength of 2 states states
    '''
    test_file = "nasqm_flu_1.out"
    result = amber_out.find_nasqm_excited_state(test_file)
    print(result)
    assert result == ""\
        "    2.90923223491635E+00    9.08434161983220E-01\n" \
        "    2.90923255131416E+00    9.08120295476811E-01\n" \
        "    2.90923255131440E+00    9.08120295476795E-01\n" \
        "    2.90576054156170E+00    9.12245042622513E-01\n" \
        "    2.89718863282344E+00    9.17508693665317E-01\n" \
        "    2.88542766911918E+00    9.23660450221756E-01\n"

def test_find_dipole():
    '''
    Make sure that we can get the mm dipoles
    '''
    test_string = "Ewald error estimate:   0.1964E-03" \
                  "-------------------------------------------------"\
                  "-----------------------------\n"\
                  "\n"\
                  "                  X        Y        Z     TOTAL  \n"\
                  "  MM DIPOLE    -6.487   81.075    4.482   81.458\n"\
                  "                  X        Y        Z     TOTAL  \n"\
                  "  QM DIPOLE       NaN      NaN      NaN      NaN\n"\
                  " QMMM: No. QMMM Pairs per QM atom:          289\n"\
                  "Ewald error estimate:   0.1964E-03" \
                  "-------------------------------------------------"\
                  "-----------------------------\n"\
                  "\n"\
                  "                  X        Y        Z     TOTAL  \n"\
                  "  MM DIPOLE    -6.487   81.075    4.482   87.879\n"\
                  "                  X        Y        Z     TOTAL  \n"\
                  "  QM DIPOLE       NaN      NaN      NaN      NaN\n"\
                  " QMMM: No. QMMM Pairs per QM atom:          289\n"
    input_stream = io.StringIO(test_string)
    result = amber_out.find_dipoles(input_stream)
    np.testing.assert_array_equal(result, np.array([81.458, 87.879]))


def test_find_total_energies():
    '''
    Tests the search for the total energies
    '''
    input_stream = open("nasqm_flu_1.out")
    result = amber_out.find_total_energies(input_stream)
    np.testing.assert_array_equal(result, np.array([167.2595, 167.3586, 167.9726,
                                                    168.5343, 168.3066]))

def test_find_mulliken_ground():
    '''
    Tests the search for the ground mulliken charges
    '''
    input_stream = open("mulliken.out")
    result = amber_out.find_mulliken(input_stream)
    answer = np.array([-0.117761, -0.167077, -0.117597, -0.042156, -0.156667,
                       -0.083535, -0.111534, -0.103507, -0.050007,  0.128741,
                       0.131213,  0.130706,  0.134001,  0.129848,  0.127329,
                       0.132333, -0.120314, -0.125125, -0.115139, -0.116000,
                       -0.034186, -0.120143, -0.111777, -0.046107,  0.129521,
                       0.131332,  0.137158,  0.134541,  0.127387,  0.128946,
                       -0.118025, -0.129561, -0.126849, -0.134490, -0.118479,
                       0.133080,  0.134198,  0.131878,  0.131384,  0.132439])
    np.testing.assert_array_equal(result, answer)


def test_find_number_excited_states():
    input_stream = open("nexmd.out", 'r')
    result = amber_out.find_number_excited_states(input_stream)
    answer = 3
    assert result == answer

def test_find_molecular_orbitals_sl():
    '''
    Test to see if we can find all the molecular orbitals if they exist on one line
    '''
    test_string = "   4   5.223507      0.3371488       1.307608      0.2904138E-02   1.350377    \n"\
                  "QMMM: Occupied MO Energies (eV):\n"\
                  "      -44.02369531      -38.08051618      -32.43536223      -24.87485851      -20.09194335\n"\
                  "QMMM: Virtual MO Energies (eV):\n"\
                  "       -0.22417960        0.97215825        3.43420817        3.62191473        4.07142528\n"\
                  "QMMM:\n"\
                  "QMMM: SCF Energy =      -16.27809329 KCal/mol,       -68.10754234 KJ/mol\n"
    input_stream = io.StringIO(test_string)
    result = amber_out.find_molecular_orbitals(input_stream)
    answer = " -4.40236953E+01 -3.80805162E+01 -3.24353622E+01 -2.48748585E+01 -2.00919434E+01\n"\
             " -2.24179600E-01  9.72158250E-01  3.43420817E+00  3.62191473E+00  4.07142528E+00\n"
    assert result == answer


def test_find_molecular_orbitals_ml():
    '''
    Test to see if we can find all the molecular orbitals if they exist on multiple lines
    '''
    test_string = "   4   5.223507      0.3371488       1.307608      0.2904138E-02   1.350377    \n"\
                  "QMMM: Occupied MO Energies (eV):\n"\
                  "      -44.02369531      -38.08051618      -32.43536223      -24.87485851      -20.09194335\n"\
                  "      -19.55122070      -19.23592030      -14.26529179      -14.03199539      -12.65494149\n"\
                  "      -12.36988176      -12.33845690\n"\
                  "QMMM: Virtual MO Energies (eV):\n"\
                  "       -0.22417960        0.97215825        3.43420817        3.62191473        4.07142528\n"\
                  "        5.45832964        6.75806534\n"\
                  "QMMM:\n"\
                  "QMMM: SCF Energy =      -16.27809329 KCal/mol,       -68.10754234 KJ/mol\n"
    input_stream = io.StringIO(test_string)
    result = amber_out.find_molecular_orbitals(input_stream)
    answer = " -4.40236953E+01 -3.80805162E+01 -3.24353622E+01 -2.48748585E+01"\
             " -2.00919434E+01 -1.95512207E+01 -1.92359203E+01 -1.42652918E+01"\
             " -1.40319954E+01 -1.26549415E+01 -1.23698818E+01 -1.23384569E+01\n"\
             " -2.24179600E-01  9.72158250E-01  3.43420817E+00  3.62191473E+00"\
             "  4.07142528E+00  5.45832964E+00  6.75806534E+00\n"
    open("result.txt", 'w').write(result)
    open("answer.txt", 'w').write(answer)
    assert result == answer

def test_find_scf_energies():
    '''
    Test to see if we can find all the SCF Energies
    '''
    test_string = "5.46897674        6.78304863\n"\
                  "QMMM:\n"\
                  "QMMM: SCF Energy =      -16.02468052 KCal/mol,       -67.04726331 KJ/mol\n"\
                  "QMMM: SCF Energy = Heat of formation\n"\
                  "QMMM: Virtual MO Energies (eV):\n"\
                  "       -0.20232826        0.97862004        3.44128505        3.62892427        4.08834732\n"\
                  "        5.46842837        6.78174443\n"\
                  "QMMM:\n"\
                  "QMMM: SCF Energy =      -16.03917358 KCal/mol,       -67.10790226 KJ/mol\n"\
                  "QMMM: SCF Energy = Heat of formation\n"
    input_stream = io.StringIO(test_string)
    result = amber_out.find_scf_energies(input_stream)
    answer = "-16.02468052\n-16.03917358\n"
    assert result == answer
