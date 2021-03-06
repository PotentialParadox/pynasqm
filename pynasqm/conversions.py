atomic_to_ps = 2.41888E-5
plank_ev = 4.135667696E-15
ps_to_atomic = 1.0 / atomic_to_ps
atomic_to_angstrom = 0.529177249
angstrom_to_atomic = 1.0 / atomic_to_angstrom
amber_to_angstrom_ps = 20.455
angstrom_ps_to_amber = 1.0 / amber_to_angstrom_ps
angstrom_ps_to_atomic =  ps_to_atomic / angstrom_to_atomic
amber_to_atomic = amber_to_angstrom_ps * angstrom_ps_to_atomic
atomic_to_amber = 1.0 / amber_to_atomic
atomic_to_angstrom_ps = 1.0 / angstrom_ps_to_atomic

def fs_to_ev(value):
    return plank_ev / (value * 1E-15)
