import numpy as np
import math as m
import sympy

from Reference  import REF_AEQ
from Reference  import REF_structs

def Sizing(params):
    '''
    Assignee(s): Max and Amish

    Lowkey it's 3AM and 1) I don't want to write anymore and 2) I think you guys have got a good idea of what is going on, so I'll keep it short. Let me know though if you have more questions

    Inputs
    - LPT outlet conditions (e.g. T0, P0, Mach numbers, velocities, T, P, etc.)
    - LPT outlet geometry (annulus radii and whatnot)
        - This is what I am working on at the moment, it's very much a work in progress, but you should see the one unlabeled output graphs that is the turbine annulus geometry.
        - Assume for now (this should be a very safe assumptions, i don't see why it wouldn't be true) that the turbine sizing function outputs the tip and hub radii of the LPT
          at the very last station.
    
    Outputs
    - Nozzle profile geometry (plotted in Plotting.py)
    - In Print_results.py:
        - Performance parameters such as final outlet velocity, final outlet temperatures and pressures
        - Geometric dimensions
    
    Some musings:
    - In the future, if we really wanna get all bougie with our nozzle, what if we did some chevrons and used it as an excuse for yall to learn acoustic modelling? that might be kinda cool
    - Also, chevrons look cool

    Same reminders as everyone else:
        - If you have helper functions (I'm guessing there will be some), make a new folder called "Nozzle" and put them in a new file called HELP_Nozzle.py. Turn the folder into a module. See other folder structures for reference
        - One input, one output
        - If you're ever stuck, try asking the other people working on this for help first, and if this doesn't work out, please don't hesitate to talk to me so that we can figure something out
        - AI should not be generating code that ends up in this repository. Please don't do it, or I'll just give your task to someone else who actually wants to learn.    
    '''
    pass
