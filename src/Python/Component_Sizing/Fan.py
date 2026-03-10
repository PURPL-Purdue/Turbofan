import numpy as np
import math as m
import sympy

from Reference  import REF_AEQ
from Reference  import REF_structs
from Fan        import HELP_Fan

def Sizing(params):
    '''
    Assignee(s): David and JP (The GOATs)

    Introduction and Objectives:
        Sizing of the fan and determining fan blade geometry. The fan provides the majority of the thrust for the engine by accelerating a lot of mass a relatively small amount.
        The first step for sizing the fan is to do a pitchline velocity triangle determination at the mean inlet radius of the LP compressor.
        This way, we can determine the flow characteristics at the inlet face of the LP compressor and give it actual numbers.
        I encourage you to look through the pitchline calculations for both the axial compressor as well as the axial turbine for inspiration.
        If you're confused about how to calculate velocity triangles for this section, talk to me and I will help you out.

    Inputs:
    - Inlet nacelle outlet conditions
    - Target conditions to reach at the fan outlet/compressor inlet
    - Geometric and material constraints (e.g. maximum diameter, maximum yield stresses)
    - Design pressure ratio

    Outputs:
    - Determination of inlet nacelle type
    - Inlet and nacelle geometric design
        - Flow path profile defined mathematically and geometrically
        - Inlet lip geometry (thickness, bluntness)
    - Thermodynamic calculation for inlet exit conditions
        - T0, P0, T, P, rho

    Note: As of now, the task list only reflects current actionable items for velocity triangle deterination along the LPC meanline
    Direct Tasks:
    - We need to know what the LPC meanline radius is in order to find fan velocity triangles along that radius. Find a way to determine the compressor LPC meanline radius.
      Remember, the LPC sizing hasn't happened at this point in the code (fan comes before LPC, with fan ouputs going into LPC inputs).
    - Once we know the LPC meanline radius, we should be able to create velocity triangles for the inlet and outlet of the fan along that radius

    Associated Tasks:
    - In Plotting.py: plot the velocity triangles at the inlet and outlet
    - In Print_Results.py display critical values including, but not necessarily limited to: T0, P0, T, P, and rho for both the fan inlet and outlet

    Resources:
    - Existing code for meanline calculations in the compressor and turbine sections
    - Farokhi Chapter 8, up to 8.6.2
        - As you'll see in the book, this is geared towards compressors, not fans, but the section about velocity triangles is good with nice diagrams if you're comfused.
        
    Reminders:
        - If you have helper functions (I'm guessing there will be some), put them in HELP_Fan,py, which can be found in the Fan folder
            - A note on this: as you know, pitchline calculations already exist for turbine and compressor within the code. Before you make a new helper function, see if it already exists and see how you can adapt it for this
        - One input, one output    
        - If you're ever stuck, try asking the other people working on this for help first, and if this doesn't work out, please don't hesitate to talk to me so that we can figure something out
        - AI should not be generating code that ends up in this repository. Please don't do it, or I'll just give your task to someone else who actually wants to learn.
    '''

    T0 = REF_structs.StationTnP.T0

    # local station 1 velocity triangle calculations
    htftrr = 0.2    # hub to fan tip radius ratio (arbitrary) 
    U_tip = M_tip_max * a_tip # tangential velocity of fan tip based on max mach number we want
    omega = U_tip / r_tip # angular velocity
    r_hub = r_tip * htftrr # hub radius
    r_LPC_tip = m.sqrt((r_tip2 + bypassRatio * r_hub2)/(bypassRatio + 1)) # LPC tip radius based on bypass ratio and fan tip radius
    r_mean = (r_LPC_tip + r_hub) / 2
    U_m = r_mean * omega # **
    alpha_1 = m.atan(U_m / V_1) # **
    w_magnitude = v_1 / m.sin(alpha_1) # **

    # local station 3 velocity triangle calculations
    Cp = gamma / (gamma - 1) * R_constant
    C_theta2 = Cp * (T02 - T01) / U_m
    alpha_2 = m.atan((U_m - C_theta2) / V_1) # **
    w_magnitude_2 = v_1 / m.sin(alpha_2) # **


    pass