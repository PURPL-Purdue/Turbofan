import numpy as np
import math as m
import sympy

from Reference  import REF_AEQ
from Reference  import REF_structs
from Fan        import HELP_Fan


def mass_flow(rho, V, r):
    m_dot = 0
    for i in range(len(rho) - 1):
        rho_avg = (rho[i] + rho[i + 1]) / 2
        V_avg = (V[i] + V[i + 1] / 2)
        area = m.pi * ((r[i] + r[i + 1])**2 - (r[i])**2)
        m_dot += rho_avg * V_avg * area

    return m_dot

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
    
    gamma           = params.gamma
    Cp              = params.Cp_cLP
    bypassRatio     = params.bypass
    M_tip_inlet_max = params.M_tip_inlet_max
    C_1             = params.C_1
    R               = params.R
    M_1             = params.M_1                # inlet mach number
    T01             = params.T01
    P01             = params.P01
    mdot_1          = params.mdot_1
    np              = params.np # polytropic efficiency (decimal)
    Pr              = params.Pr #input pressure ratio
    Tr              = m.pow(Pr, (gamma - 1) / gamma * np)
    constantRad     = params.constantRad # ("hub", "tip", or "mean"); determines what characteristic remains constant for inlet annulus calculation


    #check muhehehe
    T1 = T01 * REF_AEQ.T_T0(gamma, M_1) # static temp
    a1 = REF_AEQ.a(gamma, R, T1) # speed of sound
    
    # ======== Inlet Annulus ========
    rho01 = P01 / (R * T01)
    A_1 = mdot_1 / (rho01 * C_1)

    if constantRad == "hub":
        
        r_hub_1 = params.r_hub_1
        r_tip_1 = m.sqrt((A_1 / m.pi) + r_hub_1**2)
        htftrr = r_hub_1 / r_tip_1

    elif constantRad == "tip":

        r_tip_1 = params.r_tip_1
        r_hub_1 = m.sqrt(r_tip_1**2 - (A_1 / m.pi))
        htftrr = r_hub_1 / r_tip_1

    elif constantRad == "mean":
    
        htftrr = params.htftrr
        r_hub_1 = m.sqrt((A_1 * htftrr**2) / (m.pi * (1 - htftrr**2)))
        r_tip_1 = r_hub_1 / htftrr

    else:
        print("Check for typos goober")


    # local station 1 velocity triangle calculations :thumbsup:
    U_tip_inlet = M_tip_inlet_max * a1 # tangential velocity of fan tip based on max mach number we want
    omega = U_tip_inlet / r_tip_1 # angular velocity
    r_mean = (r_hub_1 + r_tip_1) / 2 # constant
    # ========================================================================================
    
    
    #fix code attempt!!! (numerical integration or something)
    # ======== Mass Flow Along Blade Span ========
    num_increments = 100 # input desired number of dividends along blade span (higher num = higher accuracy)
    T02 = Tr * T01
    P02 = Pr * P01
    rho02 = P02 / (R * T02)
    z_2m = C_1

    r_hub_2 = r_hub_1   # temporary initial values
    r_tip_2 = r_tip_1   # temporary initial values
    mdot_2 = 0          # temporary initial values
    rho_2_vec = np.zeros((1, num_increments + 1))
    C_2_vec = np.zeros((1, num_increments + 1))
    r_2_vec = np.zeros((1, num_increments + 1))
    massflowConditionMet = False

    while not massflowConditionMet:
        
        dr = (r_tip_2 - r_hub_2) / num_increments
        r_i = r_hub_2
        for i in range(num_increments + 1):
            
            # C along span
            U_i = omega * r_i
            Ctheta_2i = Cp * (T02 - T01) / U_i
            C_i = m.sqrt(Ctheta_2i**2 + z_2m**2)
            C_2_vec[i] = C_i
    
            # rho along span
            T2_i = T02 - (C_i**2 / (2 * Cp))
            rho_2i = rho02 * m.pow((T2_i / T02), (1 / (gamma - 1)))
            rho_2_vec[i] = rho_2i
            
            # annulus radii along span
            r_i += dr
            r_2_vec[i] = r_i
    
        # total station 2 mass flow
        mdot_2 = mass_flow(rho_2_vec, C_2_vec, r_2_vec)
        
        if abs(mdot_2 - mdot_1) <= 0.001:
            massflowConditionMet = True

        else:

            # iterate r_hub and r_tip based on constant r_mean
            A_2_current = m.pi * (r_tip_2**2 - r_hub_2**2)
            A_2_actual = A_2_current * mdot_1 / mdot_2
            h = A_2_actual / (4 * m.pi * r_mean)
            r_hub_2 = r_mean - h
            r_tip_2 = r_mean + h

    j = 0
    coreFlow = 0
    bypassConditionMet = False
    while not bypassConditionMet:
        rho_avg = (rho_2_vec[j] + rho_2_vec[j + 1]) / 2
        V_avg = (C_2_vec[j] + C_2_vec[j + 1]) / 2
        area = m.pi * ((r_2_vec[j] + r_2_vec[j + 1])**2 - (r_2_vec[j])**2)
        coreFlow += rho_avg * V_avg * area

        if (((mdot_2 - coreFlow) / coreFlow) >= bypassRatio):
            bypassConditionMet = True

        else:
            j += 1
    
    r_LPC_tip = r_2_vec[j]
    # ========================================================================================

    # TODO: confirm whether these calculations are for fan outlet or compressor inlet (r_mean may differ?)
    r_mean = (r_LPC_tip + r_hub_2) / 2
    U_m = r_mean * omega # **
    alpha_1 = m.atan(U_m / C_1) # **
    w_magnitude = C_1 / m.sin(alpha_1) # **

    # local station 3 velocity triangle calculations
    # Cp = gamma / (gamma - 1) * R
    C_theta2 = Cp * (T02 - T01) / U_m
    alpha_2 = m.atan((U_m - C_theta2) / C_1) # **
    w_magnitude_2 = C_1 / m.sin(alpha_2) # **


    pass