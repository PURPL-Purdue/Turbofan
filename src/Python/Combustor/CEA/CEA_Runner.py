import os
import sys
import math as m
import numpy as np
from dataclasses import dataclass
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), ".")))
os.environ["CEA_USE_SITE_PACKAGES"] = '1'
from Python.Combustor.CEA import CEA_Wrap as CEA
    
#run CEA
def Run_CEA(t3, tFuel, p3):
    oxid = CEA.Oxidizer(name = "Air",temp = t3, wt = 100) #Oxidizer Specs
    fuel = CEA.Fuel(name = "Jet-A(L)", temp = tFuel, wt = 100) #Fuel Specs

    problem = CEA.HPProblem(pressure = p3, massf = True, pressure_units = "bar") #Setup CEA
    problem.set_phi(1) #Define phi

    data = problem.run(fuel, oxid) #extract data

    return data

# use data.variable for data extraction- all can be found at 
# https://github.com/civilwargeeky/CEA_Wrap?tab=readme-ov-file#hp-specified-enthalpy-and-pressure-and-tp-specified-temperature-and-pressure
# potential variable replacements:
# p - pressure
# t - temperature
# h - enthalpy
# cp - specific heat capacity
# mw - molecular weight of products
# son- sonic velocity