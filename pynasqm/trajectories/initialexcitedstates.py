'''
get_n_initial_states_w_laser_energy_and_fwhm generates a list of initial excited states
using information supplied by abs_spectra, which is a file in the format with each line [e1 f1 e2 e2].
'''
import numpy as np
import math
import random
from pynasqm.conversions import fs_to_ev

def get_n_initial_states_w_laser_energy_and_fwhm(n, abs_spectra, laser_energy, fwhm):
    probabilities = get_probabilities_from(abs_spectra, laser_energy, fwhm)
    return [choose(probabilities) + 1 for _ in range(n)]

def get_probabilities_from(abs_spectra, laser_energy, fwhm):
    energies, strengths = get_energies_and_strenghts(abs_spectra)
    return calc_probabilities(laser_energy, fwhm, energies, strengths)

def calc_probabilities(laser_energy, fwhm, energies, strengths):
    return normalize(calc_raw_probabilities(laser_energy, fwhm, energies, strengths))

def normalize(v):
    norm = np.sum(v)
    return  0 if norm == 0 else v / norm

def calc_raw_probabilities(laser_energy, fwhm, energies, strenghts):
    return [calc_raw_probability(laser_energy, fwhm, e, s) for e, s in zip(energies, strenghts)]

def convert_laserfwhm_to_sigma2(fwhm):
    alpha = 2.35482 # fwhm = alpha * sigma
    fc_fwhm = pow(alpha,2) * fs_to_ev(fwhm) / math.sqrt(2)
    return pow(alpha*fs_to_ev(fwhm),2)/2

def calc_raw_probability(laser_energy, fwhm, energy, strength):
    f = strength
    pi = math.pi
    s2 = convert_laserfwhm_to_sigma2(fwhm)
    w = laser_energy
    e = energy
    return f * 1.0 / math.sqrt(2.0 * pi * s2) * math.exp(-pow(e-w,2) / (2*s2))

def get_energies_and_strenghts(abs_spectra):
    return split_energies_and_strengths(get_averages(abs_spectra))

def get_averages(abs_spectra):
    return np.average(np.loadtxt(abs_spectra), axis=0)

def split_energies_and_strengths(average_values):
    return average_values[::2], average_values[1::2]

def create_choice_list(probabilities, start=0):
    if probabilities != []:
        return [start] + create_choice_list(probabilities[1:], start + probabilities[0])
    return [start]

def choose(probabilities):
    return len([x for x in create_choice_list(probabilities) if x < random.uniform(0,1)]) - 1
