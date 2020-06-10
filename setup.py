from setuptools import setup

setup(
   name='pynasqm',
   version='1.0',
   description='Scripts a modules to interface with nasqm',
   author='Dustin Tracy',
   author_email='dtracy.uf@gmail.com',
   packages=['pynasqm', 'pynasqm.trajectories', 'pynasqm.nmr'],  #same as name
   install_requires=['numpy', 'matplotlib', 'pytraj'], #external packages as dependencies
   scripts=[
            'scripts/nasqm.py',
            'scripts/hist_spectra_lifetime.py',
            'scripts/naesmd_spectra_plotter.py',
            'scripts/find_spectra_shift.py',
            'scripts/amber_nexmd_converter.py',
            'scripts/print_quantum_coeffs.py',
            'scripts/population_plotter.py',
            'scripts/population_fitter.py',
           ]
)
