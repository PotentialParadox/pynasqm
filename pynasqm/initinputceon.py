initinputceon = ""\
"&qmmm\n"\
"!***** Geometry Optimization\n"\
"maxcyc=0, ! Number of cycles for geometry optimization, 0-none [0]\n"\
"ntpr=1, ! Print results every ntpr cycles [1]\n"\
"grms_tol=1.0d-2, ! Tolerance in eV/A (derivatives) [1.0d-2]\n"\
"!***** Ground-State and Output Parameters\n"\
"qm_theory='AM1', ! Integral type, check Amber’s SQM for more options [AM1]\n"\
"scfconv=1.0d-8, ! Ground-state SCF convergence criteria, eV [1.0d-6]\n"\
"verbosity=1, ! QM/MM output verbosity (0-minimum, 5-maximum)\n"\
"! [1 for dynamics and optimization, 5 for others]\n"\
"printdipole=1, ! (0) Unrelaxed transitions, (1) Unrelaxed transitions plus\n"\
"! total molecular, or (2) Unrelaxed/relaxed transitions plus\n"\
"! total molecular [1 for dynamics, 2 for optimization and single-point]\n"\
"printbondorders=0, ! (0) No or (1) Yes [0]\n"\
"! *** UNDER DEVELOPMENT, DO NOT USE ***\n"\
"density_predict=0, ! (0) None, (1) Reversible MD,\n"\
"! or (2) XL-BOMD [0] *** ALL ARE UNDER DEVELOPMENT, DO NOT USE ***\n"\
"itrmax=300, ! Max SCF iterations for ground state\n"\
"! (negative to ignore convergence) [300]\n"\
"!***** Excited-State Parameters\n"\
"exst_method=1, ! CIS (1) or RPA (2) [1]\n"\
"dav_guess=1, ! Restart Davidson from (0) Scratch, (1) Previous,\n"\
"! or (2) XL-BOMD [1] *** (2) IS UNDER DEVELOPMENT, DO NOT USE ***\n"\
"ftol0=1.0d-5, ! Acceptance tolerance (|emin-eold|) [1.0d-5]\n"\
"ftol1=1.0d-5, ! Acceptance tolerance for residual norm [1.0d-5]\n"\
"! *** UNDER DEVELOPMENT, DO NOT USE ***\n"\
"dav_maxcyc=200, ! Max cycles for Davidson diagonalization\n"\
"! (negative to ignore convergence) [100]\n"\
"printcharges=0, ! Print (1) or do not print (0) Mulliken charges of QM atoms [0]\n"\
"calcxdens=.false., ! Print (.true.) or do not print (.false.)\n"\
"! excited-to-excited transition dipole moments [.false.]\n"\
"!***** Solvent Models and External Electric Fields\n"\
"solvent_model=0, ! (0) None, (1) Linear response, (2) Vertical excitation,\n"\
"! or (3) State-specific [0]\n"\
"potential_type=1, ! (1) COSMO or (2) Onsager [1]\n"\
"onsager_radius=2, ! Onsager radius, A (system dependent) [2]\n"\
"ceps=10, ! Dielectric constant, unitless [10]\n"\
"linmixparam=1, ! Linear mixing parameter for vertical excitation\n"\
"! or state-specific SCF calculation [1]\n"\
"cosmo_scf_ftol=1.0d-5, ! Vertical excitation or state-specific\n"\
"! SCF tolerance, eV [1.0d-5]\n"\
"doZ=.false., ! Use relaxed (.true.) or unrelaxed (.false) density for\n"\
"! vertical excitation or state-specific COSMO or Onsager [.false.]\n"\
"index_of_refraction=100, ! Dielectric constant for linear response\n"\
"! solvent in excited-state, unitless [100] *** UNDER DEVELOPMENT, DO NOT USE ***\n"\
"qm_ewald=0, ! Not Supported Yet\n"\
"qm_pme=0, ! Not Supported Yet\n"\
"EF=0, ! (0) None or (1) Electric field in ground- and excited-state [0]\n"\
"Ex=0, ! Electric field vector X, eV/A [0]\n"\
"Ey=0, ! Electric field vector Y, eV/A [0]\n"\
"Ez=0, ! Electric field vector Z, eV/A [0]\n"\
"&endqmmm\n"\
"&moldyn\n"\
"!***** General Parameters\n"\
"rnd_seed=19345, ! Seed for the random number generator\n"\
"bo_dynamics_flag=1, ! (0) Non-BO or (1) BO [1]\n"\
"exc_state_init=0, ! Initial excited state (0 - ground state) [0]\n"\
"n_exc_states_propagate=0, ! Number of excited states [0]\n"\
"!***** Dynamics Parameters\n"\
"time_init=0.0, ! Initial time, fs [0.0]\n"\
"time_step=0.1, ! Time step, fs [0.1]\n"\
"n_class_steps=0, ! Number of classical steps [1]\n"\
"n_quant_steps=4, ! Number of quantum steps for each classical step [4]\n"\
"moldyn_deriv_flag=1, ! (0) None, (1) Analytical, or (2) Numerical [1]\n"\
"num_deriv_step=1.0d-3, ! Displacement for numerical derivatives, A [1.0d-3]\n"\
"rk_tolerance=1.0d-7, ! Tolerance for the Runge-Kutta propagator [1.0d-7]\n"\
"!***** Non-Adiabatic Parameters\n"\
"decoher_type=2, ! Type of decoherence: Reinitialize (0) Never,\n"\
"! (1) At successful hops, (2) At successful plus frustrated hops...\n"\
"! (3) Persico/Granucci, or (4) Truhlar [2]\n"\
"! *** (3) AND (4) ARE UNDER DEVELOPMENT, DO NOT USE ***\n"\
"decoher_e0=0.0, ! Decoherence parameter E0, Hartrees [0.1]\n"\
"! (only for decoher_type = 3 or 4) *** UNDER DEVELOPMENT, DO NOT USE ***\n"\
"decoher_c=0.0, ! Decoherence parameter C, unitless [0.1]\n"\
"! (only for decoher_type = 3 or 4) *** UNDER DEVELOPMENT, DO NOT USE ***\n"\
"dotrivial=1, ! Do unavoided (trivial) crossing routine (1) or not (0) [1]\n"\
"quant_step_reduction_factor=2.5d-2, ! Quantum step reduction factor [2.5d-2]\n"\
"!***** Thermostat Parameters\n"\
"therm_type=1, ! Thermostat type: (0) Newtonian, (1) Langevin,\n"\
"! or (2) Berendsen [1] *** (2) IS UNDER DEVELOPMENT, DO NOT USE ***\n"\
"therm_temperature=300, ! Thermostat temperature, K [300]\n"\
"therm_friction=20, ! Thermostat friction coefficient, 1/ps [20]\n"\
"berendsen_relax_const=0.4, ! Bath relaxation constant for Berendsen\n"\
"! thermostat, ps [0.4] *** UNDER DEVELOPMENT, DO NOT USE ***\n"\
"heating=0, ! Equilibrated (0) or heating (1) [0]\n"\
"! *** UNDER DEVELOPMENT, DO NOT USE ***\n"\
"heating_steps_per_degree=100, ! Number of steps per degree\n"\
"! during heating [100] *** UNDER DEVELOPMENT, DO NOT USE ***\n"\
"!***** Output & Log Parameters\n"\
"verbosity=3, ! NEXMD output verbosity (0-minimum, 3-maximum)\n"\
"! [2 for dynamics, 3 for optimization and single-point]\n"\
"out_data_steps=1, ! Number of steps to write data [1]\n"\
"out_coords_steps=10, ! Number of steps to write the restart file [10]\n"\
"out_data_cube=0, ! Write (1) or do not write (0) view files to generate cubes [0]\n"\
"out_count_init=0, ! Initial count for view files [0]\n"\
"&endmoldyn\n"\
"&coord\n"\
"&endcoord\n"\
"&veloc\n"\
"&endveloc\n"\
"&coeff\n"\
"&endcoeff\n"\
