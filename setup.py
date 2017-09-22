from setuptools import setup

setup(
   name='pynasqm',
   version='1.0',
   description='Scripts a modules to interface with nasqm',
   author='Dustin Tracy',
   author_email='dtracy.uf@gmail.com',
   packages=['pynasqm'],  #same as name
   install_requires=['numpy', 'matplotlib'], #external packages as dependencies
   scripts=[
            'scripts/nasqm.py',
            'scripts/hist_spectra_lifetime.py',
            'scripts/naesmd_spectra_plotter.py',
            'scripts/find_spectra_shift.py',
           ]
)
