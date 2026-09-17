import os
import sys
import math as m
import numpy as np
from dataclasses import dataclass
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), ".")))
import CMB_Air_Distribution as air_dist
import CEA.CEA_Runner as CEA

# def combustor_sizing(params):
t3              = 600 #params.t3 # K
t4              = 1000 #params.t4 # K
tSecondary      = 1800 #params.tSecondary # K
mDot3           = 7 #params.mDot3 # kg/s
fuelAirRatio    = 0.06# params.fuelAirRatios
cp3             = 0.06 #params.cp3 # kJ/kg-

print(f"t3: {t3} K")

data = CEA.Run_CEA(t3, 300, 5.515806, 10) # K
tPrim = data.t # temp of primary zone 
cpPrimary = data.cp 
print(f"{data.prod_c}")

# Calculates the air distribution to each section of the combustor
# See CMB_Air_Distribution.py for more details on the function and its inputs/outputs
pzd, szd, dzd = air_dist.Calc_Air_Distribution(t3, t4, tSecondary, tPrim, mDot3, fuelAirRatio, cp3, cpPrimary)

print(f"Primary Zone Mass Flow Fraction: {pzd:.3f}")
print(f"Secondary Zone Mass Flow Fraction: {szd:.3f}")
print(f"Dilution Zone Mass Flow Fraction: {dzd:.3f}")

#return