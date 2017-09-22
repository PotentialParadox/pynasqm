'''
Determine the shift between two spectra
'''
import math
import numpy as np

def find_ev_max(A):
    '''
    Find the eV value corresponding to the maximum intensity
    '''
    max_value = -math.inf
    max_ev = 0
    for i in range(len(A)):
        if A[i, 2] > max_value:
            max_value = A[i, 2]
            max_ev = A[i, 0]
    return max_ev


def find_nm_max(A):
    '''
    Find the nm value corresponding to the maximum intensity
    '''
    max_value = -math.inf
    max_nm = 0
    for i in range(len(A)):
        if A[i, 2] > max_value:
            max_value = A[i, 2]
            max_nm = A[i, 1]
    return max_nm


def find_shift(A, unit):
    '''
    Find the eV shift between two spectra
    '''
    spectra_1 = A[:,0:3]
    spectra_2 = A[:,[0, 1, 3]]
    unit_1 = None
    unit_2 = None
    if unit == "ev":
        unit_1 = find_ev_max(spectra_1)
        unit_2 = find_ev_max(spectra_2)
    if unit == "nm":
        unit_1 = find_nm_max(spectra_1)
        unit_2 = find_nm_max(spectra_2)
    return float("{:16.8f}".format(unit_2 - unit_1))
