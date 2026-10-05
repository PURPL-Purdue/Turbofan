import numpy as np
import math as m
import sympy

from Reference  import REF_AEQ
from Reference  import REF_structs
from Compressor import HELP_Radial_Compressor

def Radial_Compressor_Sizing(params):
    '''
    Assignee(s): Stefan and Trey

    Intro/Objectives
        Sizing and blade geometry generation for the HPC, which will be a single stage radial compressor. The hope is to move away from CFTurbo for this project.
        Sizing includes much of the same stuff as what we did for the current engine. This means finding major dimensions and defining the meridional flow path of the air.
        Blade geometry generation is the very cooked part, where we want to generate our own 3D impeller blade geometry. I think this part will be perhaps some of the most
        difficult coding of the whole project, but I think it is doable. For now, the task at hand is sizing first, and once that is figured out, we can move onto blade geometry.

    Inputs:
    - LPC flow outlet conditions (e.g. T0, P0, T, P, rho, Mach numbers, velocities, angles, etc.)
    - Maximum impeller tip radius
    - Impeller tip tangential velocity

    Outputs:
    - Flow path geometry
    - Impeller main dimensions (e.g. tip radius, inlet radius, axial length, blade heights, etc.)

    Direct Tasks:
    - From the inputs, determine velocity triangles
    - Size the impeller
        - Axial length
        - Radii dimensions

    Associated Tasks
    - In Plotting.py, plot the flow path geometry
    - In Print_Results.py, display the impeller main dimensions

    Resources:
    - Aungier, Centrifugal Compressors, Chapters 4, 5, 6
        - None of these chapters are onerously long, so please read all of them
    - CFTurbo manual
        - The CFTurbo manual is nice in that it often cites where it gets its math from. Reading through the documentation for CFTurbo impeller design is a good way to see how they do it.

    Reminders:
        - If you have helper functions (I'm guessing there will be some), put them in HELP_Radial_Compressor,py, which can be found in the Compressor folder
        - One input, one output
        - If you're ever stuck, try asking the other people working on this for help first, and if this doesn't work out, please don't hesitate to talk to me so that we can figure something out
        - AI should not be generating code that ends up in this repository. Please don't do it, or I'll just give your task to someone else who actually wants to learn.
    '''

    C1              = params.C1             # inlet absolute velocity (m/s)
    U1              = params.U1             # inlet tangential velocity (m/s)
    w1              = params.w1             # inlet relative velocity (m/s)
    P1              = params.P1             # inlet pressure
    T1              = params.T1             # inlet temp
    P2              = params.P2             # outlet pressure
    alpha1          = params.alpha1         # inlet flow angle
    r_tip_max       = params.r_tip_max      # max tip radius
    r_hub           = params.r_hub          # hub radius
    m_dot           = params.m_dot          # mdot
    nu              = params.nu             # overall efficiency
    rho             = params.rho            # density

    gamma           = params.gamma          # cp/cv
    e_T             = params.e_T            # efficiency?

    # compressor outlet temp? - (9.15)
    T_t2 = (P2/P1)*T1**((gamma*e_T)/(gamma-1))






    pass