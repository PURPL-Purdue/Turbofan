import numpy as np
import math as m
import sympy

from Reference  import REF_AEQ
from Reference  import REF_structs

def Sizing(params):
    '''
    Assignee(s): Mark

    Introduction and Objectives:
        Sizing of the inlet nacelle for our engine. The inlet captures a streamtube of air and directs it to the fan inlet face. The primary purpose is to manipulate the
        inlet/ambient air into a state suitable for ingestion into the fan e.g. reasonable mach number, desired temperature and pressure, etc.

    Inputs:
    - Ambient (incoming) conditions
    - Target conditions to reach at the end of the inlet
    - Geometric constraints (e.g. axial length)

    Outputs:
    - Determination of inlet nacelle type
    - Inlet and nacelle geometric design
        - Flow path profile defined mathematically and geometrically
        - Inlet lip geometry (thickness, bluntness)
    - Thermodynamic calculation for inlet exit conditions
        - T0, P0, T, P, rho

    Direct Tasks:
        - Research different types of inlet geometries and choose a path to proceed with
            - Check with me about chosen inlet geometry before starting to code
        - Code:
            - Determine suitable axial length
            - Implement chosen profile for inlet profile (could be a type of spline or other mathematical distribution/geometry)
                - Both internal flow path geometry as well as lip geometry
    
    Associated Tasks:
        - In Plotting.py: create plots of the inlet nacelle geometry
        - In Print_Results.py: display critical values including, but not necessarily limited to: T0, P0, T, P, rho, geometric lengths

    Resources:
    - Farokhi Chapter 6
        - Note: content from 6.10 and onwards concerns supersonic inlets, and is therefore not particularly applicable to our engine. Feel free to learn about it, but it's probably not directly useful for us

    Reminders:
        - If you have helper functions, make a new folder/module titled "Inlet" and put them there (see other folders for structure examples)
        - One input, one output
        - If you're ever stuck, please don't hesitate to talk to me so that we can figure something out
        - AI should not be generating code that ends up in this repository. Please don't do it, or I'll just give your task to someone else who actually wants to learn.
    '''
    pass