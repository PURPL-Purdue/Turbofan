import numpy as np
import math as m
import sympy

from Reference  import REF_AEQ
from Reference  import REF_structs
from Compressor import HELP_Axial_Compressor
from Turbine    import HELP_Turbine
from Fan        import HELP_Fan

def Fan_Sizing(params):
    '''
    Fan "Meanline" Sizing

    The first step for sizing the fan is to do a pitchline velocity triangle determination at the mean inlet radius of the LP compressor.
    This way, we can determine the flow characteristics at the inlet face of the LP compressor and give it actual numbers
    I encourage you to look through the pitchline calculations for both the axial compressor as well as the axial turbine for inspiration.
    If you're confused about how to calculate velocity triangles for this section, talk to me (Marvel) and I will help you out.

    The inputs for this function should be our known inlet temperatures and pressures from the cycle analysis output as well as the gas characteristics
    such as Cp, R, that sort of stuff. The output should be velocity triangles for the two stations, one at the fan blade inlet and one at the fan blade outlet.
    '''
    pass

def Axial_Compressor_Sizing(params):
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

    Places to look and get started:
    Start by reading through Farokhi 8.14 and 8.14.1. I want us to implement as much of the stuff listed in 8.14 as possible.
    A lot of it already is included in the code, so please first try to fully understand what is already here before adding new stuff.
    Notable things I would like you to include in your section on blade design include:
    - 1D blade root stress calcs and the blade taper calcs [5-7]
    - 1D Bending stress calcs [15]
    - Subsonic blade geometry generation [Section 8.14.1]
        - I know this section is very cursory and not very in-depth. I would like us to focus on just subsonic blades for now, which ig the book
          only has like one sentence about, and it just talks about NACA-65. This lack of detail is understandable given the intent of the book,
          but is unfortunate regardless, so I would you like to do some additional reading into compressor blade design. Please go to the reading
          folder of the turbojet Google Drive, find "Axial Compressor Book" (also by le goat Aungier lmao) and read Chapter 4. Before you start
          implementing blade geometry code, please talk to me first and explain what approach you have chosen and why, as well as what your plan is.
    
    Please start with the 1D blade root stress and bending stress calcs, as it should be an easier, more introductory gateway into the whole sizing code.
    I would encourage the use of separate functions for the blade root stress and bending stress calculations. I've already put definitions for them in
    HELP_Compressor, though feel free to add more if it works better.

    The stuff on the lines below until line 260 are the very beginnings of blade design I put in way at the beginning. You might see some familiar things
    that are mentioned in the numbered list in Farokhi 8.14, and that's cuz that's where I got them from.

    Whatever you end up doing in this code, please try to keep other existing work as unmodified as possible, and if you do end up changing things, that's ok,
    just please communicate with whoever wrote it first before making big changes. That said, feel free to mess with whatever is in here until Line 260 as you wish,
    with the exception of the three lines labeled PLEASE DON'T TOUCH.
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

def Turbine_Sizing(params):
    '''
    Design Criteria:
    - Constant axial velocity
    - Cooled with compressor bleed air (set "ep" to 0 for uncooled turbine)
    - Choked first stator exit (M_2m = 1.1)
    - First stator alpha2 = 60 degrees
    '''

    m_dot_t         = params.m_dot_t    # Turbine total mass flow, kg/s, air plus fuel
    m_dot_c         = params.m_dot_c   # Compressor mass flow, just air
    rpm             = params.RPM      # RPM

    T0_2            = params.T0_2comp  # Compressor inlet total temp
    T0_3            = params.T0_3comp      # Compressor outlet total temp
    T0_4m           = params.T0_4m        # Turbine inlet total temperature, K
    P0_4m           = params.P0_4m     # Turbine inlet total pressure,    Pa 

    r_mean_c        = params.r_mean_c      # Comrpessor pitchline radius, meters

    m_dot_cool      = params.m_dot_cool     # Cooling air bleedoff mass flow, kg/s
    T0_cool         = params.T0_cool       # Cooling air temperature, kelvin
    P0_cool         = params.P0_cool   # Cooling air pressure, Pa

    M_a             = params.M_a
    P0_0m           = params.P0_0m
    T0_0m           = params.T0_0m

    Cp_c            = params.Cp_c
    Cp_t            = params.Cp_t
    gamma_c         = params.gamma_c
    gamma_t         = params.gamma_t

    eta_mech        = params.eta_mech
    ep              = params.ep

    # Fan stuff
    m_dot_f         = params.m_dot_f
    Cp_f            = params.Cp_f
    T0_15           = params.T0_15

    # First stage design decisions
    alpha_1m        = np.radians(params.alpha_1m)
    alpha_2m        = np.radians(params.alpha_2m)
    Mc_2m           = params.Mc_2m                 # Slightly supersonic stator nozzle exit
    Mw_3Rm          = params.Mw_3Rm                # TODO find justification for this

    # Multistage design decisions
    Mc_2m_default   = params.Mc_2m_default               # Just barely not choking the flow at stator nozzle exit
    Mw_3Rm_default  = params.Mw_3Rm_default               # TODO find justification for this
    r_mean = r_mean_c

    ang_vel = rpm * 2*np.pi / 60 # Angular velocity, rad/s
    R_t = (gamma_t-1)*Cp_t/gamma_t

    # ======== Whole Turbine Calcs (absolute station numbers) ========
    power_c = m_dot_c * Cp_c * (T0_3-T0_2)          # Power required by compressor          | TODO get exact power equation, this is just an approximation
    power_f = 0 if m_dot_f == None else m_dot_f * Cp_f * (T0_2-T0_15)
    req_power_t = power_c + power_f/eta_mech                          # Turbine power generation requirement  | Accounts for mechanical losses

    # Using symbolic equations to solve for the exit temperature of the whole turbine
    T0_5_cooled_sym = sympy.symbols("T0_5_cooled_sym")                                                                  # Creating symbolic variable
    eqn1 = sympy.Eq(m_dot_c * ((1-ep)*Cp_t*(T0_4m-T0_5_cooled_sym) + ep*Cp_c*(T0_cool-T0_5_cooled_sym)), req_power_t)   # Defining equation
    T0_5m_cooled = sympy.solve(eqn1, T0_5_cooled_sym)[0]                                                                # Solving

    # Total temperature drop across entire turbine
    deltaT_total = T0_4m - T0_5m_cooled

    # ======== Pitchline Staging ========
    # Setting up lists to contain staging data
    multistage_velocity_triangles = []
    multistage_info = []

    # Initial stage
    velocity_triangles_s1, info_s1, powerReqMet = HELP_Turbine.Turbine_Stage_Pitchline(
        True,
        Mc_2m,
        Mw_3Rm,
        alpha_1m,
        alpha_2m,
        T0_4m,
        P0_4m,
        r_mean_c,
        ang_vel,
        gamma_t,
        R_t,
        Cp_t,
        m_dot_t,
        0,
        req_power_t
        )
    multistage_velocity_triangles.append(velocity_triangles_s1)
    multistage_info.append(info_s1)
    
    total_power_generated = multistage_info[0].power

    # Subsequent staging
    stage_idx = 1
    while not powerReqMet:
        # Calculate triangles and info for new stage
        velocity_triangles, info, powerReqMet = HELP_Turbine.Turbine_Stage_Pitchline(
            False,
            Mc_2m_default,
            Mw_3Rm_default,
            multistage_velocity_triangles[stage_idx-1].alpha_3m,
            multistage_velocity_triangles[stage_idx-1].z_3m,
            multistage_info[stage_idx-1].T0_3m,
            multistage_info[stage_idx-1].P0_3m,
            r_mean,
            ang_vel,
            gamma_t,
            R_t,
            Cp_t,
            m_dot_t,
            total_power_generated,
            req_power_t
            )
        
        # Keep track of total power generated up to this point
        total_power_generated += info.power
        # Add to info lists
        multistage_velocity_triangles.append(velocity_triangles)
        multistage_info.append(info)
        # Updating loop
        stage_idx += 1
    
    stage_powers = [stage_info.power for stage_info in multistage_info]
    excess_power_margin = (total_power_generated - req_power_t)/req_power_t * 100
    R = Cp_t * (gamma_t-1)/gamma_t

    HELP_Turbine.Turbine_Annulus_Sizing(
        multistage_velocity_triangles,
        multistage_info,
        m_dot_t,
        gamma_t,
        R,
        r_mean_c)

    AT_OUT = REF_structs.Turbine_OUT(
        multistage_velocity_triangles,
        multistage_info,
        total_power_generated,
        req_power_t,
        power_c,
        power_f,
        excess_power_margin
    )

    return AT_OUT