from dataclasses import dataclass
import numpy as np
import math as m
import time

import REF_AEQ
import REF_structs
import Station_Thermo
import Component_Sizing
import Plotting as plot
import matplotlib.pyplot as plt

# Initializing dataclasses for component efficiencies, specific heat ratios, and pressure ratios
eta = REF_structs.ByComponent(
                None, # Ambient
                0.94, # Diffuser
                0.85, # Fan
                0.98, # Fan Nozzle
                0.75, # LP Compressor
                0.75, # HP Compressor
                1.00, # Burner
                0.90, # HP Turbime
                0.90, # LP Turbine
                0.98  # Nozzle
)
gamma = REF_structs.ByComponent(
                1.4,  # Ambient
                1.4,  # Diffuser
                1.4,  # Fan
                1.4,  # Fan Nozzle
                1.4,  # LP Compressor
                1.4,  # HP Compressor
                1.3,  # Burner
                1.32, # HP Turbine
                1.32, # LP Turbine
                1.34  # Nozzle
)
Pr = REF_structs.ByComponent(
                None,       # Ambient
                None,       # Diffuser
                1.6,        # Fan
                None,       # Fan Nozzle
                5,          # LP Compressor
                5,          # HP Compressor
                0.95,          # Burner
                None,       # HP Turbine
                None,       # LP Turbine
                None        # Nozzle
)

# ======== Ambient Conditions and General Engine Parameters ========
cycle_params = {
    "eta"    : eta,             # nondimensional
    "gamma"  : gamma,           # nondimensional
    "Pr"     : Pr,              # nondimensional
    "T_0"    : 298,             # TODO | At ambient, v=0, so T0 = T
    "P_0"    : 101300,          # TODO | At ambient, v=0, so P0 = P
    "M_f"    : 0.0,             # nondimensional
    "Ra"     : 287,             # TODO
    "Rp"     : 287,             # TODO
    "QR"     : 45000000,        # TODO
    "bypass" : 2.89,               # nondimensional
    "combustion_temp": 1300,    # TODO
}
thermo, Cps, thrust, eta_calc, m_dot_core = Station_Thermo.thermoCalcs(cycle_params)

compressor_params = {
    "gamma"       : gamma.cLP,
    "Cp_cLP"      : Cps.cLP,
    "T0_1"        : thermo.S2.T0,
    "P0_1"        : thermo.S2.P0,
    "Pr"          : Pr.cLP,
    "e_c"         : 0.99,            # Polytropic Efficiency
    "httrr"       : 0.8,            # Hub-to-tip radius ratio
    "deHaller"    : 0.72,           # De Haller's Criterion value
    "min_Re"      : 300000,         # For blade sizing
    "mu_kin"      : 1.46e-5,        # Kinematic viscosity
    "alpha_1m"    : 30,             # Inlet absolute flow angle, in degrees
    "Mz_1m"       : 0.45,           # Inlet axial mach number
    "U_tip_inlet" : 350,            # Inlet rotor tip speed, m/s
    "m_dot_core"  : m_dot_core
}

# compressor_info = Component_Sizing.Compressor_Sizing(compressor_params)
# turbine_info = Component_Sizing.Turbine_Sizing(turbine_params)

plt.show()