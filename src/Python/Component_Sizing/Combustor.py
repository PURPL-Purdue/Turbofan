import numpy as np
import math as m
import sys
import os
import sympy

from Reference      import REF_AEQ
from Reference      import REF_structs
from Combustor      import CMB_Air_Distribution
from Combustor.CEA  import CEA_Runner as CEA

def Sizing(params):
    t3              = REF_structs.params.t3 # K
    t4              = REF_structs.params.t4 # K
    tSecondary      = REF_structs.params.tSecondary # K
    mDot3           = REF_structs.params.mDot3 # kg/s
    fuelAirRatio    = params.fuelAirRatio
    cp3             = params.cp3 # kJ/kg-K

    data = CEA.Run_CEA(t3, tSecondary, cp3) # K
    tPrim = data.t # temp of primary zone 
    cpPrimary = data.cp 

    # Calculates the air distribution to each section of the combustor
    # See CMB_Air_Distribution.py for more details on the function and its inputs/outputs
    pzd, szd, dzd = air_dist.Calc_Air_Distribution(t3, t4, tSecondary, tPrim, mDot3, fuelAirRatio, cp3, cpPrimary)

    print(f"Primary Zone Mass Flow Fraction: {pzd:.3f}")
    print(f"Secondary Zone Mass Flow Fraction: {szd:.3f}")
    print(f"Dilution Zone Mass Flow Fraction: {dzd:.3f}")

    return
    pass