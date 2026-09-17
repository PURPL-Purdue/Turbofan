# 'pip install CoolProp' if not done already
import CoolProp.CoolProp as CoolProp
import CEA.CEA_Runner as CEA
import numpy as np
import pyfluids as pf
from pyfluids import Mixture, FluidsList, Input

# Create a simple linear mixing rule for the CO2 and Xenon pair
##CoolProp.apply_simple_mixing_rule('Ar', 'Xe', 'linear')

# Now evaluate the 50/50 mixture density at 300K and atmospheric pressure
# = CoolProp.PropsSI('Dmass','T',300,'P',101325,'Ar[0.4]&Xe[1e-5]')

#print(x)

t3              = 600 #params.t3 # K
t4              = 1000 #params.t4 # K
tSecondary      = 1800 #params.tSecondary # K
mDot3           = 7 #params.mDot3 # kg/s
fuelAirRatio    = 0.06# params.fuelAirRatios
cp3             = 0.6 #params.cp3 # kJ/kg-

data = CEA.Run_CEA(400, 300, 5.515806, 1) # K
tPrim = data.t # temp of primary zone 

mixture = Mixture([FluidsList.Water, FluidsList.Ethanol], [60, 40]).with_state(
    Input.pressure(200e3), Input.temperature(4)
)
print(mixture.density)  # 883.3922771627963

"""
# Pull the element types from data.prod_c and put them in a list
element_types = []
for comp in data.prod_c:
    element_types.append(comp.strip())

element_percentages = []
for i in range(len(element_types)):
    element_percentages.append(data.prod_c[element_types[i]])

mixture = ''
for i in range(len(element_types)):
    mixture += element_types[i] + '[' + str(element_percentages[i]) + ']'
    if i < len(element_types) - 1:
        mixture += '&'
"""