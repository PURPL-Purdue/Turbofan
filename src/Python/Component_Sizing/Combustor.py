import os
import sys
import math as m
import numpy as np
from dataclasses import dataclass
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), ".")))
from Python.Reference import REF_AEQ
from Python.Reference import REF_structs
import Python.Combustor.CMB_Air_Distribution as Air_Dist
import Python.Combustor.CEA.CEA_Runner as CEA

def Sizing(params):
    t3              = params.t3 # K
    t4              = params.t4 # K
    tSecondary      = params.tSecondary # K
    tFuel           = params.tFuel # K
    p3              = params.p3 # Pa
    mDot3           = params.mDot3 # kg/s
    phi             = 1 # equivalence ratio, set to 1 for now since we don't have a fuel flow rate input
    cp3             = params.cp3 # kJ/kg-

    data = CEA.Run_CEA(t3, tFuel, p3 / 100000, phi) # K
    tPrimary = data.t # temp of primary zone 
    cpPrimary = data.cp

    fuelAirRatio = (phi * 1 / 15) # kg fuel / kg air, convert from g fuel / kg air

    # Calculates the air distribution to each section of the combustor
    # See CMB_Air_Distribution.py for more details on the function and its inputs/outputs
    pzd, szd, dzd = Air_Dist.Calc_Air_Distribution(t3, t4, tSecondary, tPrimary, mDot3, fuelAirRatio, cp3 / 1000, cpPrimary)

    print(f"Inputs: \n{params}")
    print(f"Data: \n{data}")

    print(f"Primary Zone Mass Flow Fraction: {pzd:.3f}")
    print(f"Secondary Zone Mass Flow Fraction: {szd:.3f}")
    print(f"Dilution Zone Mass Flow Fraction: {dzd:.3f}")

    # Combustor output struct (ADD MORE OUTPUTS AS NECESSARY)
    CMB_OUT = REF_structs.Combustor_OUT(
        pzd, 
        szd, 
        dzd,
        mDot3 * (1 + fuelAirRatio), # kg/s
        p3,
        fuelAirRatio
    )

    return CMB_OUT