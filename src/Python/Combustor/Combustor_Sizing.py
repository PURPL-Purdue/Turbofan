import os
import sys
import math as m
import numpy as np
from dataclasses import dataclass
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), ".")))
import src.Python.Combustor.CMB_Air_Distribution as air_dist

t3 = 900 # K
t4 = 1300 # K;
tSecondary = 1800 # K
tFlame = 2500 # K
mDot3 = 33 # kg/s
fuelAirRatio = 0.06381831
cp3 = 1.124 # kJ/kg-K
cpPrimary = 2.6 # kJ/kg-K

# Calculates the air distribution to each section of the combustor
# See CMB_Air_Distribution.py for more details on the function and its inputs/outputs
pzd, szd, dzd = air_dist.Calc_Air_Distribution(t3, t4, tSecondary, tFlame, mDot3, fuelAirRatio, cp3, cpPrimary)

print(f"Primary Zone Mass Flow Fraction: {pzd:.3f}")
print(f"Secondary Zone Mass Flow Fraction: {szd:.3f}")
print(f"Dilution Zone Mass Flow Fraction: {dzd:.3f}")