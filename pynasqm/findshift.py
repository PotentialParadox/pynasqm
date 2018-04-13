'''
Determine the shift between two spectra
'''
import math
import numpy as np

def find_row_of_max(A):
    max_value = -math.inf
    max_row = -1
    for row, value in enumerate(A[:,-1]):
        if value > max_value:
            max_value = value
            max_row = row
    return max_row


def ev_energy(A, row):
    '''
    Find the eV value corresponding to the row
    '''
    return A[row,0]


def nm_energy(A, row):
    '''
    Find the nm value corresponding to the row
    '''
    return A[row,1]


def find_shift(file1, file2, units):
    '''
    Find the eV shift between two spectra
    '''
    DATA1 = np.loadtxt(file1)
    DATA2 = np.loadtxt(file2)
    max1 = find_row_of_max(DATA1)
    max2 = find_row_of_max(DATA2)
    energy1 = None
    energy2 = None
    if units == "ev":
        energy1 = ev_energy(DATA1, max1)
        energy2 = ev_energy(DATA2, max2)
    elif units == "nm":
        energy1 = nm_energy(DATA1, max1)
        energy2 = nm_energy(DATA2, max2)
    return energy2 - energy1


