import argparse
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pynasqm.utils
from scipy.interpolate import spline
from scipy.optimize.minpack import curve_fit

def gaus(x,a,x0,sigma):
    return a*np.exp(-(x-x0)**2/(2*sigma**2))

def fit_nonlinear(t, y, mean, sigma):
    opt_parms, _ = curve_fit(gaus, t, y, maxfev=1000, p0=[1, mean, sigma])
    A, u, s = opt_parms
    return A, u, s

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", help="The title of the graph", default="Title")
    parser.add_argument("--number_states", help="The number of states you want to include.",
                        default=1, type=int)
    parser.add_argument("--labels", "-l", help="labels of the data", nargs="+")
    parser.add_argument("--ylabel", help="labels for you y axis", default="")
    parser.add_argument("--inputfile", "-i", help="The input file", default=None)
    parser.add_argument("--outputfile", "-o", help="The output file", default=None)
    parser.add_argument("--letter", help="The letter in the paper", default="")
    parser.add_argument("--comparison", "-c",
                        help="Are you comparing spectra?",
                        default="False")
    parser.add_argument("--x_units", "-x", help="0-Ev or 1-nm", default=0, type=int)
    parser.add_argument("--range", "-r", help="Provide two numbers,"\
                        "the minimum and maximum values in the units you prefer",
                        default=[0.0, 100.0], nargs="+", type=float)
    args = parser.parse_args()
    args.comparison = pynasqm.utils.str2bool(args.comparison)
    if args.labels is None:
        args.labels = [""]*args.number_states
    data = np.loadtxt(args.inputfile)
    state_intensity_index_start = 2
    state_intensity_index_end = 2 + args.number_states
    Ys = data[:, state_intensity_index_start:state_intensity_index_end]
    X_ev = data[:, 0]
    X_nm = data[:, 1]
    plotter(args, X_ev, X_nm, Ys, args.x_units)

def plotter(args, x_ev, x_nm, ys, units):
    (x_ev, x_nm, ys) = filter_range(x_ev, x_nm, ys, args.range, units)
    ys = normalize_individuals(ys) if args.comparison else normalize_set(ys)
    x = x_ev if units == 0 else x_nm

    sns.set()
    sns.set_style("white")
    sns.set_style("ticks")
    colors = sns.color_palette()

    fig, ax = plt.subplots()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    for i in range(args.number_states):
        y = ys[:, i]
        label = args.labels[i]
        mean = sum(x*y)/sum(y)
        std = sum(y*(x-mean)**2)/sum(y)
        A, u, s = fit_nonlinear(x, y, mean, std)
        fit_y = gaus(x, A, u, s)
        ax.plot(x, y, label=label, color=colors[i])
        x_ev_max, x_nm_max = find_max_x(zip(x_ev, x_nm, fit_y))
        print("{} peak at {} eV and {} nm".format(label, x_ev_max, x_nm_max))
        x_max = x_ev_max if units == 0 else x_nm_max
        ax.axvline(x=x_max, linestyle="dashed", linewidth=1, color=colors[i])
    xlabel = "Energy (eV)" if args.x_units == 0 else "Wavelength (nm)"
    ax.set_xlabel(xlabel)
    ax.set_ylabel(args.ylabel)
    ax.legend(frameon=False, loc=1)
    ax.axes.get_yaxis().set_ticks([])
    ax.set_ylim((0, 1.5))
    ax.text(-0.05, 0.95, args.letter, transform=ax.transAxes,
            fontsize=17, fontweight='bold', va='top')
    fig.savefig(args.outputfile, bbox_inches='tight')
    plt.show()

def find_max_x(sets):
    (xev, xnm, _) = max(sets, key=lambda item: item[2])
    return xev, xnm

def normalize_individuals(ys):
    '''
    All spectra maximum values will equal
    '''
    return np.divide(ys, ys.max(0))

def normalize_set(ys):
    '''
    Spectra will keep relative magnitudes
    '''
    return np.divide(ys, np.max(ys))


def filter_range(xev_in, xnm_in, yin, my_range, units):
    y_fitered = []
    xev_filtered = []
    xnm_filtered = []
    for xev_temp, xnm_temp, y_temp in zip(xev_in, xnm_in, yin):
        x_temp = xev_temp if units == 0 else xnm_temp
        if my_range[0] <= x_temp <= my_range[1]:
            y_fitered.append(y_temp)
            xev_filtered.append(xev_temp)
            xnm_filtered.append(xnm_temp)
    return (np.array(xev_filtered), np.array(xnm_filtered), np.array(y_fitered))



main()
