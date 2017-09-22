import numpy as np
from math import exp


def get_gaus_point_energy_value(energy, fwhm, gauss_index, n_gauss):
    # The real energy value will be the center value.
    # The outer indexes will be the real energy + or - 2 * fwhm.
    # The possible return array thus looks like
    # | E@-2fwhm | .. | E | .. | E@2fwhm |
    # Energy is the energy from the input
    # fwhm is the full width at half max given as a parameter
    # Gauss index is the current index we're returning
    # n_gauss is the number of total indexes
    return energy - (2.0 * fwhm) + ((gauss_index+1) * 4.0 * fwhm / n_gauss)


def calculate_exponential(energy_max, strength, sigma, gaus_point_energy):
    # Strength is the oscillator strength from the input file
    # The energy max is the original energy from the input file
    # Sigma is the sigma that was defined previously in the program
    # Gaus_point energy is the value of the energy that we extrapolated
    # from the the original energy and an assumed normalized curve
    w = strength
    u = energy_max
    s = sigma
    x = gaus_point_energy
    return (w / u**2) * exp((-(x - u)**2) / (2 * s**2))


def print_line(fo, ev_energy, nm_energy, weighted_state_intensities, total_intensity):
    line = "{: 8.3f}{: 18.10f}".format(ev_energy, nm_energy)
    for intensity in weighted_state_intensities:
        line += "{: 18.10f}".format(intensity)
    line += "{: 18.10f}\n".format(total_intensity)
    fo.write(line)


def calculate_spectra(n_states, n_gauss, fwhm, n_bins, x_min, x_max, file_in, file_out):

    divisor = 0.02

    sigma = fwhm / 2.35482

    # Rows will correspond to time steps while columns (0, 1)_state
    # are frequency and strengths
    data = np.loadtxt(file_in)

    strengths = np.zeros((n_states, n_bins))
    total_strength = 0

    for time_step in range(len(data)):
        for state in range(n_states):
            energy = data[time_step][2*state]
            strength = data[time_step][2*state+1]
            # We will take each energy point and spread its corresponding strength across adjacent energy values
            # based on an assumed normal distribution.
            for gauss_point in range(n_gauss):
                # First get the energy value within our range from -2fwhm to +2fwhm
                gaus_point_energy = get_gaus_point_energy_value(energy, fwhm, gauss_point, n_gauss)
                # Second turn that energy point into an index that we can use for our histogram
                x_index = int(gaus_point_energy/divisor) + 1
                # Third calculate how much strength will be appropriate for this index
                appropriated_strength = calculate_exponential(energy, strength, sigma, gaus_point_energy)
                # Add to index
                strengths[state, x_index] += appropriated_strength
                # Keep track of total oscillator strength
                total_strength += appropriated_strength

    fo = open(file_out, 'w')
    for x_index in range(int(x_min/divisor), int(x_max/divisor)):
        ev_energy = x_index * divisor - divisor / 2
        nm_energy = 1E7 / (ev_energy * 8.06554465E3)
        weighted_state_intensities = np.divide(strengths[:, x_index], total_strength)
        total_intensity = np.sum(strengths[:, x_index]) / total_strength
        print_line(fo, ev_energy, nm_energy, weighted_state_intensities, total_intensity)


