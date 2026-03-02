## Helper functions for CMB_Air_Distribution.py

from dataclasses import dataclass
import numpy as np
import math as m

'''
-------------------------Description------------------------
Calculates the specific heat of the next zone based on the mass flows,
specific heats, and temperatures of both the previous and next zones.
---------------------------Inputs---------------------------
Vars            Descriptions                        Units
------------------------------------------------------------
mDotLast        mass flow of the previous zone      kg/s
mDotNext        mass flow of the next zone          kg/s
cpLast          specific heat of the previous zone  kJ/kg-K
cp3             specific heat of air at t3          kJ/kg-K
---------------------------Outputs--------------------------
Vars            Descriptions                        Units
------------------------------------------------------------
cpNext          specific heat of the next zone      kJ/kg-K
------------------------------------------------------------
'''
def Calc_CP_Next(mDotLast, mDotNext, cpLast, cp3):
    return (mDotLast * cpLast + mDotNext * cp3) / (mDotLast + mDotNext)


'''
-------------------------Description------------------------
Calculates the temp of the next zone based on the mass flows,
specific heats, and temperatures of both the previous zone and 
the mass flow of air at t3.
---------------------------Inputs---------------------------
Vars            Descriptions                        Units
------------------------------------------------------------
mDotLast        mass flow of the previous zone      kg/s
mDotIn          mass flow of the next zone          kg/s
cpLast          specific heat of the previous zone  kJ/kg-K
cp3             specific heat of air at t3          kJ/kg-K
tLast           temperature of the previous zone    K
t3              temperature of the air at t3        K
---------------------------Outputs--------------------------
Vars            Descriptions                        Units
------------------------------------------------------------
tNext           temperature of the next zone        K
------------------------------------------------------------
'''
def Calc_T_Next(mDotLast, mDotIn, cpLast, cp3, tLast, tNext, t3):
    cpNext = Calc_CP_Next(mDotLast, mDotIn, cpLast, cp3)
    tNext = (mDotLast * cpLast * tLast + mDotIn * cp3 * t3) / ((mDotLast + mDotIn) * cpNext)
    return tNext