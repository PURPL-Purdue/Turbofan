import numpy as np
import math as m
import sympy

from Reference  import REF_AEQ
from Reference  import REF_structs
from Compressor import HELP_Axial_Compressor


def Sizing(params):
    gamma           = params.gamma
    Cp              = params.Cp_cLP
    T0_1m           = params.T0_1
    P0_1m           = params.P0_1
    Pr_total        = params.Pr
    e_c             = params.e_c
    httrr           = params.httrr
    deHaller        = params.deHaller
    min_Re          = params.min_Re
    mu_kin          = params.mu_kin
    alpha_1m        = np.radians(params.alpha_1m)
    Mz_1m           = params.Mz_1m
    M_tip_inlet     = params.M_tip_inlet_max
    m_dot           = params.m_dot_core

    # Compressor inlet conditions
    Mc_1m = Mz_1m/np.cos(alpha_1m)

    # Inlet Static Pressure and Temperature
    T_1m = T0_1m*REF_AEQ.T_T0(gamma, Mc_1m)
    P_1m = P0_1m*REF_AEQ.P_P0(gamma, Mc_1m)

    # Inlet flow characteristics
    R = (gamma-1)*Cp/gamma
    rho_1m = P_1m/(R*T_1m)
    a_1m = m.sqrt((gamma-1)*Cp*T_1m)
    z_1m = Mz_1m*a_1m
    C_1m = Mc_1m*a_1m

    # Initial inlet annulus geometry, assume constant spanwise distributions
    A_inlet = m_dot/rho_1m/z_1m
    r_tip_inlet = np.sqrt(A_inlet/(np.pi*(1-httrr**2)))
    r_hub_inlet = r_tip_inlet*httrr

    # Compressor exit conditions
    Tr_total = Pr_total**((gamma-1)/(e_c*gamma))

    P0_exit_m = P0_1m * Pr_total  # at midspan
    T0_exit_m = T0_1m * Tr_total  # at midspan

    alpha_exit_m = alpha_1m   # repeating stage | at midspan
    z_exit_m = z_1m           # design choice   | at midspan
    C_exit_m = C_1m

    T_exit_m = T0_exit_m - C_exit_m**2/(2*Cp)  # | at midspan

    a_exit_m = m.sqrt((gamma-1)*Cp*T_exit_m)
    Mz_exit_m = z_exit_m/a_exit_m
    Mc_exit_m = Mz_exit_m/m.cos(alpha_exit_m)

    P_exit_m = P0_exit_m*REF_AEQ.P_P0(gamma, Mc_exit_m)  # | at midspan
    rho_exit_m = P_exit_m/(R*T_exit_m)

    # Exit annulus geometry
    A_exit = m_dot/rho_exit_m/z_exit_m

    r_mean_1 = (r_tip_inlet + r_hub_inlet)/2
    h = A_exit / (4 * m.pi * r_mean_1)

    r_hub_exit = r_mean_1 - h
    r_tip_exit = r_mean_1 + h

    error = 1
    first = True
    U_tip_inlet = M_tip_inlet*a_1m
    while error > 0.01:
        if not first:
            U_tip_inlet = U_tip_inlet - 0.5
        # ======== Pitchline calculations ========
        # Design choices TODO
        solidity_rotor = 1
        solidity_stator = 1.25

        ang_vel = U_tip_inlet/r_tip_inlet
        rpm = ang_vel * 30 / np.pi

        # Station 1 stuff
        U_1m = U_tip_inlet * (r_mean_1/r_tip_inlet)
        Ctheta_1m = z_1m*np.tan(alpha_1m)
        Wtheta_1m = U_1m - Ctheta_1m
        beta_1m = -np.atan(Wtheta_1m/z_1m)
        W_1m = z_1m / np.cos(beta_1m)
        Mw_1m = W_1m/a_1m

        # Station 2 stuff
        U_2m = U_1m        # Initial Approximation, true if we adjust both hub and shroud
        z_2m = z_1m        # Design chioce

        W_2m = W_1m*deHaller      # De Haller
        beta_2m = np.acos(z_2m/W_2m)
        Wtheta_2m = z_2m*np.tan(beta_2m)
        Ctheta_2m = U_2m-Wtheta_2m
        
        C_2m = np.sqrt(z_2m**2 + Ctheta_2m**2)
        alpha_2m = np.atan(Ctheta_2m/z_2m)

        phi_2m = z_2m/U_2m
        psi_2m = 1 + phi_2m*(np.tan(-beta_2m)-np.tan(alpha_1m))

        T0_2m = T0_1m + U_1m*(Ctheta_2m-Ctheta_1m)/Cp
        T_2m  = T0_2m - C_2m**2/(2*Cp)
        a_2 = np.sqrt((gamma-1)*Cp*T_2m)

        Mc_2m = C_2m/a_2
        Mw_2m = W_2m/a_2
        Mz_2m = z_2m/a_2

        temp_rise_total = T0_exit_m - T0_1m
        temp_rise_per_stage = T0_2m - T0_1m
        num_stages_actual = temp_rise_total/temp_rise_per_stage
        
        if first:
            target = np.floor(num_stages_actual)
            first = False
        
        error = (num_stages_actual - target)/target
        # print("tip_inlet: {:5.2f}     temp_rise: {:5.2f}     Ctheta_2m: {:5.2f}     Ctheta_1m: {:5.2f}     Ctheta 2-1: {:5.2f}     Wtheta_2m: {:5.2f}     Wtheta_1m: {:5.2f}".format(U_tip_inlet, temp_rise_per_stage, Ctheta_2m, Ctheta_1m, Ctheta_2m-Ctheta_1m, Wtheta_2m, Wtheta_1m))

    num_stages = int(np.round(num_stages_actual, 0))

    num_stations = num_stages*2 + 1

    # Station 3 stuff
    C_3m = C_1m
    W_3m = W_1m
    U_3m = U_1m
    z_3m = z_1m
    Mc_3m = Mc_1m
    Mw_3m = Mw_1m
    Mz_3m = Mz_1m
    Ctheta_3m = Ctheta_1m
    Wtheta_3m = Wtheta_1m
    alpha_3m = alpha_1m
    beta_3m = beta_1m

    # Stage metrics
    degR_m = 1 - (Ctheta_1m + Ctheta_2m) / (2*U_1m)
    D_mr = HELP_Axial_Compressor.D_factor(W_1m, W_2m, Ctheta_1m, Ctheta_2m, solidity_rotor)
    D_ms = HELP_Axial_Compressor.D_factor(C_2m, C_3m, Ctheta_2m, Ctheta_3m, solidity_stator)

    RVT = REF_structs.FullVelTriInfo(
                    C_1m, C_2m, C_3m,
                    W_1m, W_2m, W_3m,
                    U_1m, U_2m, U_3m,
                    z_1m, z_2m, z_3m,

                    Mc_1m, Mc_2m, Mc_3m,
                    Mw_1m, Mw_2m, Mw_3m,
                    Mz_1m, Mz_2m, Mz_3m,
                    
                    Ctheta_1m, Ctheta_2m, Ctheta_3m,
                    Wtheta_1m, Wtheta_2m, Wtheta_3m,
                    
                    alpha_1m, alpha_2m, alpha_3m,
                    beta_1m,  beta_2m,  beta_3m,
                    )
    
    StageInfo = {
        "degR_m" : degR_m,
        "D_mr"   : D_mr,
        "D_ms"   : D_ms,
        "phi_2m" : phi_2m,
        "psi_2m" : psi_2m,
    }

    # Per Stage State
    r_hub_vec = [1 for i in range(num_stages+1)]
    r_tip_vec = [1 for i in range(num_stages+1)]
    rho_m_vec = [1 for i in range(num_stages+1)]
    T0_stages = [1 for i in range(num_stages+1)]
    P0_stages = [1 for i in range(num_stages+1)]
    Tr_stages = [1 for i in range(num_stages)]
    Pr_stages = [1 for i in range(num_stages)]
    
    T0_stages[0] = T0_1m
    P0_stages[0] = P0_1m

    r_hub_vec[0] = r_hub_inlet
    r_tip_vec[0] = r_tip_inlet

    T0_current = T0_1m
    for i in range(num_stages):
        T0_next = T0_current + temp_rise_per_stage
        Tr_stages[i] = T0_next / T0_current
        Pr_stages[i] = Tr_stages[i]**(gamma*e_c/(gamma-1))
        T0_stages[i+1] = T0_next
        P0_stages[i+1] = P0_stages[i]*Pr_stages[i]
        T0_current = T0_next

    for i in range(num_stages+1):
        r_hub_vec[i], r_tip_vec[i], rho_m_vec[i] = HELP_Axial_Compressor.annulus_adjust(T0_stages[i], P0_stages[i], R, gamma, m_dot, RVT.z_1m, RVT.Mc_1m, r_mean_1)

    # Compressor Thermodynamics Total Metrics
    Pr_total_actual = np.prod(Pr_stages)
    Tr_total_actual = T0_stages[-1]/T0_stages[0]
    P0_rise_total = P0_stages[-1] - P0_stages[0]

    '''
    Blade Design

    Assignee(s): Josie and Nishan

    Intro/Objective
        Sizing of the compressor blade main dimensions and generation of the compressor blade geometry. Also includes determinatinon of blade taper ratios and includes a calculation of
        blade root and bending stresses. The intent is for these blade stress functions to act as a quick automatic check during the compressor sizing process to make sure that the
        blades are structurally sound.

    Resources:
    - Farokhi 8.14 (blade stress)
        - I want us to implement as much of the stuff listed in 8.14 as possible.
        - A lot of it already is included in the code, so please first try to fully understand what is already here before adding new stuff.
        - This section has a cursory introduction to simple blade stress calculations. Let me know if it's not enough and you want more stuff to read into.
    - Farokhi 8.14.1 (blade design)
        - I know this section of the book is very surface level and not very in-depth. I would like us to focus on just subsonic blades for now, which ig the book
          only has like one sentence about, and it just talks about NACA-65. This lack of detail is understandable given the intent of the book,
          but is unfortunate regardless, so I would you like to do some additional reading into compressor blade design outside of this book.
    - Aungier, Axial Compressor Design, Chapter 4 (blade design)
        - Go to the reading folder of the turbojet Google Drive, find "Axial Compressor Book"
        - This chapter has a lot more detail about blade geometry design, and I encourage you to read all of it before choosing a path to go down
        - Before you start implementing blade geometry code, please talk to me first and explain what approach you have chosen and why, as well as what your plan is.
    
    Note: As of now, the task list only reflects current actionable items for blade stress stuff
    Direct Tasks 
    - 1D blade root stress calcs and the blade taper calcs (Points 5-7 in Farokhi 8.14)     | Josie
    - 1D Bending stress calcs (Points 5-7 in Farokhi 8.14)                                  | Nishan
    
    Note 1: Please start with the 1D blade root stress and bending stress calcs, as it should be an easier, more introductory gateway into the whole sizing code.
    I would encourage the use of separate functions for the blade root stress and bending stress calculations. I've already put definitions for them in
    HELP_Compressor, though feel free to add more if it works better.

    Note 2: The stuff on the lines below until the long line of dashes are the very beginnings of blade design I put into the code a long time ago. You might see some familiar things
    that are mentioned in the numbered list in Farokhi 8.14, and that's cuz the book is where I got these numbers from.

    Note 3: Whatever you end up doing in this code, please try to keep other existing work above and below this little chunk as unmodified as possible, and if you do end up changing things, that's ok,
    just please communicate with whoever wrote it first before making big changes. That said, feel free to mess with whatever is in here until the dashed lined as you wish,
    with the exception of the three lines labeled PLEASE DON'T TOUCH.

    Reminders:
        - If you have helper functions (I'm guessing there will be some), put add them to HELP_Axial_Compressor,py, which can be found in the Compressor folder. It doesn't really matter where you put them, ig just add them to the end of the file
        - One input, one output
        - If you're ever stuck, try asking the other people working on this for help first, and if this doesn't work out, please don't hesitate to talk to me so that we can figure something out
        - AI should not be generating code that ends up in this repository. Please don't do it, or I'll just give your task to someone else who actually wants to learn.
    '''
    some_output = HELP_Axial_Compressor.Blade_Root_Stress()
    some_output = HELP_Axial_Compressor.Blade_Bending_Stress()

    # Supersonic rotor design
    ttc_m = 0.065 # PLEASE DON'T TOUCH
    min_chord_m = min_Re*mu_kin/W_1m       # meters, minimum chord to get reynolds PLEASE DON'T TOUCH
    chord_m = 1.0*min_chord_m # PLEASE DON'T TOUCH

    i = np.degrees(ttc_m)
    dev_ang_m = np.abs(beta_2m+beta_1m) / 4 * np.sqrt(solidity_rotor) + 2

    # Camber angle
    K_1m = -beta_1m - i
    K_2m = beta_2m - dev_ang_m
    camber_m = K_1m - K_2m

    stagger_ang = -beta_1m - camber_m/2 - i

    num_blades_rotor = 2 * np.pi * r_mean_1 / chord_m

    # Subsonic stator design
    T0_2m = T0_1m + U_1m*(Ctheta_2m-Ctheta_1m)/Cp
    T_2m  = T0_2m - C_2m**2/(2*Cp)
    a_2 = np.sqrt((gamma-1)*Cp*T_2m)

    # ------------------------------------------------------------------------------------------------ #

    Mc_2m = C_2m/a_2

    AC_FF = HELP_Axial_Compressor.Compressor_Free_Vortex(RVT, r_hub_vec, r_tip_vec, ang_vel, degR_m, rho_m_vec, Cp, R, T0_stages, m_dot, e_c, gamma)
    r_mean_1 = (AC_FF.r_hub_vec_full[0] + AC_FF.r_tip_vec_full[0]) / 2

    AC_OUT = REF_structs.Compressor_OUT(
        RVT,
        AC_FF,
        P0_stages,
        T0_stages,
        Pr_stages,
        StageInfo,
        num_stages_actual,
        num_stages,
        rpm,
        chord_m,
        Pr_total,
        Pr_total_actual,
        Tr_total,
        Tr_total_actual,
        P0_rise_total,
        temp_rise_total,
        temp_rise_per_stage,
        U_tip_inlet,
        r_mean_1
    )

    return AC_OUT