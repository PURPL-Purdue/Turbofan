## CMB_Combustor_Outlet_Temp.py
## Calculates the outlet temp of the combustor based on the air distribution and fuel flow
'''
---------------------------Inputs---------------------------
Vars            Descriptions                        Units
------------------------------------------------------------
pzd             primary zone mass flow fraction     unitless
szd             secondary zone mass flow fraction   unitless
dzd             dilution zone mass flow fraction    unitless
mDot3           mass flow of air                    kg/s
mDotFuel        mass flow of fuel                   kg/s
t3              temperature from compressor         K
t4              desired temperature to turbine      K    
t_flame         flame temperature                   K
equiv_ratio     equivalence ratio                   unitless
--------------------------------------------------------
'''
'''
---------------------------Outputs--------------------------
Vars            Descriptions                        Units
------------------------------------------------------------
tOutlet         Outlet temperature of combustor     K
------------------------------------------------------------
'''
from dataclasses import dataclass
import numpy as np
import math as m
import Plotting as plot

def Calc_Outlet_Temp(pzd, szd, dzd, mDot3, mDotFuel, t3, t4, t_flame):
    # Calculate the mass flow rates for each zone
    mDotPrimary = pzd * mDot3
    mDotSecondary = szd * mDot3
    mDotDilution = dzd * mDot3

    # Calculate the total mass flow to the turbine
    mDotTotal = mDot3 + mDotFuel

    # Calculate the outlet temperature using energy balance
    tOutlet = ((mDotPrimary + mDotFuel) * t_flame + mDotSecondary * t3 + mDotDilution * t3) / mDotTotal

    return tOutlet