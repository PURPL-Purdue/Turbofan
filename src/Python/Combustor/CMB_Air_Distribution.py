from dataclasses import dataclass
import numpy as np
import math as m
import matplotlib.pyplot as plt

'''
-------------------------Description------------------------
Calculates the specific heat of the next zone based on the mass flows,
specific heats, and temperatures of both the previous and next zones.
---------------------------Inputs---------------------------
Vars            Descriptions                            Units
------------------------------------------------------------
mDotLast        mass flow of the previous zone          kg/s
mDotNext        mass flow of the next zone              kg/s
cpLast          specific heat of the previous zone      kJ/kg-K
cp3             specific heat of air from station 3     kJ/kg-K
---------------------------Outputs--------------------------
Vars            Descriptions                            Units
------------------------------------------------------------
cpNext          specific heat of the next zone          kJ/kg-K
------------------------------------------------------------
'''
def Calc_CP_Next(mDotLast, mDotNext, cpLast, cp3):
    return (mDotLast * cpLast + mDotNext * cp3) / (mDotLast + mDotNext)


'''
-------------------------Description------------------------
Calculates the temp of the next zone based on the mass flows,
specific heats, and temperatures of both the previous zone and 
the mass flow of air from station 3.
---------------------------Inputs---------------------------
Vars            Descriptions                            Units
------------------------------------------------------------
mDotLast        mass flow of the previous zone          kg/s
mDotIn          mass flow of the next zone              kg/s
cpLast          specific heat of the previous zone      kJ/kg-K
cp3             specific heat of air from station 3     kJ/kg-K
tLast           temperature of the previous zone        K
t3              temperature of the air at t3            K
---------------------------Outputs--------------------------
Vars            Descriptions                            Units
------------------------------------------------------------
tNext           temperature of the next zone            K
------------------------------------------------------------
'''
def Calc_T_Next(mDotLast, mDotIn, cpLast, cp3, tLast, tNext, t3):
    cpNext = Calc_CP_Next(mDotLast, mDotIn, cpLast, cp3)
    tNext = (mDotLast * cpLast * tLast + mDotIn * cp3 * t3) / ((mDotLast + mDotIn) * cpNext)
    return tNext

'''
-------------------------Description------------------------
Calculates the air distribution to each section of the combusstor
using energy balance equations and iterating through the mass flow fractions
until the desired temperatures are met in the secondary and dilution zones
---------------------------Inputs---------------------------
Vars            Descriptions                            Units
------------------------------------------------------------
t3              temperature from compressor             K
t4              desired temperature to turbine          K    
tSecDesired     temperature at which reaction stops     K
tFlame          flame temperature                       K
mDot3           mass flow of air                        kg/s
fuelAirRatio    fuel to air ratio                       unitless
cpPrimary       specific heat of primary zone           kJ/kg-K
cp3             specific heat of air from station 3     kJ/kg-K 
---------------------------Outputs--------------------------
Vars            Descriptions                            Units
------------------------------------------------------------
pzd             primary zone mass flow fraction         unitless
szd             secondary zone mass flow fraction       unitless
dzd             dilution zone mass flow fraction        unitless
------------------------------------------------------------
'''
def Calc_Air_Distribution(t3, t4, tSecDesired, tPrimary, mDot3, fuelAirRatio, cp3, cpPrimary):
    pzd = 1 # fraction of mass flow to the primary zone (unitless)
    szd = 0 # fraction of mass flow to the secondary zone (unitless)
    pz_sz_ratio = 0 # ratio of primary zone mass flow to secondary zone mass flow (unitless)
    dzd = 0 # fraction of mass flow to the dilution zone (unitless)
    tSecondary = tSecDesired + 1 # temperature of secondary zone (K)
    tOutlet = tPrimary + 1 # initial guess for outlet temperature of combustor (K)
    inc = 0.001 # increment for iterating through the fractions

# primary and secondary zone loop
# finds the optimal ratio between the primary and secondary zones to meet the desired secondary zone temperature
    while tSecondary > tSecDesired:
        pzd -= inc
        szd = 1 - pzd
        mDotPrimary = pzd * mDot3 * (1 + fuelAirRatio)
        mDotSecondary = szd * mDot3
        tSecondary = Calc_T_Next(mDotPrimary, mDotSecondary, cpPrimary, cp3, tPrimary, tSecDesired, t3)

    pz_sz_ratio = pzd / szd

    while tOutlet > t4:
        dzd += inc
        szd = (1 - dzd) / (1 + pz_sz_ratio)
        mDotSecondary = szd * mDot3
        mDotDilution = dzd * mDot3
        cpSecondary = Calc_CP_Next(mDotPrimary, mDotSecondary, cpPrimary, cp3)
        tOutlet = Calc_T_Next(mDotSecondary, mDotDilution, cpSecondary, cp3, tSecondary, tOutlet, t3)
    
    pzd = szd * pz_sz_ratio

    return pzd, szd, dzd