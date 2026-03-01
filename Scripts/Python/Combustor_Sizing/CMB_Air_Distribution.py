from dataclasses import dataclass
import numpy as np
import math as m
import Plotting as plot
import matplotlib.pyplot as plt
import CMB_Combustor_Outlet_Temp as outlet_temp

## required inputs
t3 = 900 # temperature from compressor (K)
t4 = 1300 # desired temperature to turbine (K)
t_flame = 2500 # flame temperature (K)
mDot3 = 8 # mass flow of air (kg/s)
mDotFuel = 0.1 # mass flow of fuel (kg/s)

equiv_ratio = 0.5 # equivalence ratio (unitless)

pzd = 0 # fraction of mass flow to the primary zone (unitless)
szd = 0 # fraction of mass flow to the secondary zone (unitless)
dzd = 0 # fraction of mass flow to the dilution zone (unitless)
inc = 0.01 # increment for iterating through the fractions

while pzd <= 1:
    szd = 1 - pzd

    while szd >= 0:
        dzd = 1 - pzd - szd
        outlet_t = outlet_temp.Calc_Outlet_Temp(pzd, szd, dzd, mDot3, mDotFuel, t3, t4, t_flame)

        if outlet_t >= t4: # outputs when desired temp is reached
            pzd -= inc
            szd = 1 - pzd
            dzd = 1 - pzd - szd
            print(f" Outlet temperature: {outlet_t:.2f}, pzd {pzd :.4f}, szd: {szd:.4f}, dzd: {dzd:.4f}")
            pzd = 2
            szd = -1

        temp_outlet = outlet_t
        szd -= inc

    pzd += inc