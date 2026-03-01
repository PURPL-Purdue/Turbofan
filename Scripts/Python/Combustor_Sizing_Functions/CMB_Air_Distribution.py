from dataclasses import dataclass
import numpy as np
import math as m
import matplotlib.pyplot as plt
import HELP_Air_Distribution as helper

def Calc_Air_Distribution(t3, t4, tSecDesired, tFlame, mDot3, fuelAirRatio, cp3, cpPrimary):
    '''
    ---------------------------Inputs---------------------------
    Vars            Descriptions                        Units
    ------------------------------------------------------------
    t3              temperature from compressor         K
    t4              desired temperature to turbine      K    
    tSecDesired     temperature at which reaction stops K
    tFlame          flame temperature                   K
    mDot3           mass flow of air                    kg/s
    fuelAirRatio    fuel to air ratio                   unitless
    cpPrimary       specific heat of primary zone       kJ/kg-K
    cp3             specific heat of air at t3          kJ/kg-K 
    
    ------------------------------------------------------------
    '''
    '''
    ---------------------------Outputs--------------------------
    Vars            Descriptions                        Units
    ------------------------------------------------------------
    pzd             primary zone mass flow fraction     unitless
    szd             secondary zone mass flow fraction   unitless
    dzd             dilution zone mass flow fraction    unitless
    ------------------------------------------------------------
    '''
    t3 = 900 # temperature from compressor (K)
    t4 = 1300 # desired temperature to turbine (K)
    tStopRxn = 1800 # Tempeartaure at which the reaction of Fuel Stops (K)
    tFlame = 2500 # flame temperature (K)
    mDot3 = 8 # mass flow of air (kg/s)
    fuelAirRatio = 0.06381831 # fuel to air ratio (unitless)
    cpPrimary = 2.5793 # specific heat of primary zone (kJ/kg-K)
    cp3 = 1.005 # specific heat of air at t3 (kJ/kg-K)

    pzd = 1 # fraction of mass flow to the primary zone (unitless)
    szd = 0 # fraction of mass flow to the secondary zone (unitless)
    pz_sz_ratio = 0 # ratio of primary zone mass flow to secondary zone mass flow (unitless)
    dzd = 0 # fraction of mass flow to the dilution zone (unitless)
    tSecondary = tSecDesired + 1 # temperature of secondary zone (K)
    tOutlet = tFlame + 1 # initial guess for outlet temperature of combustor (K)
    inc = 0.001 # increment for iterating through the fractions

    while tSecondary > tSecDesired:
        pzd -= inc
        szd = 1 - pzd
        mDotPrimary = pzd * mDot3 * (1 + fuelAirRatio)
        mDotSecondary = szd * mDot3
        tSecondary = helper.Calc_T_Next(mDotPrimary, mDotSecondary, cpPrimary, cp3, tFlame, tStopRxn, t3)

    pz_sz_ratio = pzd / szd

    print(f"Primary to Secondary Zone Mass Flow Ratio: {pz_sz_ratio:.3f}")

    while tOutlet > t4:
        dzd += inc
        szd = (1 - dzd) / (1 + pz_sz_ratio)
        mDotSecondary = szd * mDot3
        mDotDilution = dzd * mDot3
        cpSecondary = helper.Calc_CP_Next(mDotPrimary, mDotSecondary, cpPrimary, cp3)
        tOutlet = helper.Calc_T_Next(mDotSecondary, mDotDilution, cpSecondary, cp3, tSecondary, tOutlet, t3)

    pzd = szd * pz_sz_ratio

    print(f"Primary Zone Mass Flow Fraction: {pzd:.3f}")
    print(f"Secondary Zone Mass Flow Fraction: {szd:.3f}")
    print(f"Dilution Zone Mass Flow Fraction: {dzd:.3f}")