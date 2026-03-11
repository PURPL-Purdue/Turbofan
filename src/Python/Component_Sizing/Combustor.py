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

def combustor_sizing(params):
    t3              = params.t3 # K
    t4              = params.t4 # K
    tSecondary      = params.tSecondary # K
    mDot3           = params.mDot3 # kg/s
    fuelAirRatio    = params.fuelAirRatio
    cp3             = params.cp3 # kJ/kg-

    data = CEA.Run_CEA(t3, tSecondary, cp3) # K
    tPrim = data.t # temp of primary zone 
    cpPrimary = data.cp 

    # Calculates the air distribution to each section of the combustor
    # See CMB_Air_Distribution.py for more details on the function and its inputs/outputs
    pzd, szd, dzd = Air_Dist.Calc_Air_Distribution(t3, t4, tSecondary, tPrim, mDot3, fuelAirRatio, cp3, cpPrimary)

    print(f"Primary Zone Mass Flow Fraction: {pzd:.3f}")
    print(f"Secondary Zone Mass Flow Fraction: {szd:.3f}")
    print(f"Dilution Zone Mass Flow Fraction: {dzd:.3f}")

    # Combustor output struct (ADD MORE OUTPUTS AS NECESSARY)
    CMB_OUT = REF_structs.Combustor_OUT(
        pzd, 
        szd, 
        dzd,

    )

    return CMB_OUT