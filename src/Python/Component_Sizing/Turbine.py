import numpy as np
import math as m
import sympy

from Reference  import REF_AEQ
from Reference  import REF_structs
from Turbine    import HELP_Turbine

def Sizing(params):
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
    degR_m          = params.degR_m
    
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
        degR_m,
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
            degR_m,
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
