from dataclasses import dataclass, field

####################################################
#                     Turbine                      #
####################################################
@dataclass
class FullVelTriInfo:
    C_1m: float
    C_2m: float
    C_3m: float
    W_1m: float
    W_2m: float
    W_3m: float
    U_1m: float
    U_2m: float
    U_3m: float
    z_1m: float
    z_2m: float
    z_3m: float

    Mc_1m: float
    Mc_2m: float
    Mc_3m: float
    Mw_1m: float
    Mw_2m: float
    Mw_3m: float
    Mz_1m: float
    Mz_2m: float
    Mz_3m: float

    Ctheta_1m: float
    Ctheta_2m: float
    Ctheta_3m: float
    Wtheta_1m: float
    Wtheta_2m: float
    Wtheta_3m: float

    alpha_1m: float
    alpha_2m: float
    alpha_3m: float
    beta_1m: float
    beta_2m: float
    beta_3m: float

@dataclass
class Turbine_Pitchline_Results:
    multistage_velocity_triangles   : list
    multistage_info                 : list
    r_mean_vec                      : list

    total_power_generated           : float
    excess_power_margin             : float

    num_stages_target               : float

@dataclass
class Turbine_IN:
    m_dot_t         : float
    m_dot_c         : float
    RPM             : float

    T0_2comp        : float
    T0_3comp        : float
    T0_4m           : float
    P0_4m           : float

    r_mean_i        : float

    m_dot_cool      : float
    T0_cool         : float
    P0_cool         : float

    M_a             : float
    P0_0m           : float
    T0_0m           : float

    Cp_c            : float
    Cp_t            : float
    gamma_c         : float
    gamma_t         : float

    eta_mech        : float
    ep              : float

    m_dot_f         : float
    Cp_f            : float
    T0_15           : float

    alpha_1m        : float
    alpha_2m        : float
    Mc_2m           : float
    Mw_3Rm          : float

    Mc_2m_default   : float
    Mw_3Rm_default  : float
    degR_m          : float

@dataclass
class Turbine_OUT:
    initial_pitchline_res:  Turbine_Pitchline_Results
    pitchline_res:          Turbine_Pitchline_Results
    req_power:              float
    req_power_comp:         float
    req_power_fan:          float

@dataclass
class Turbine_Gen:
    IN:  Turbine_IN = field(default=(Turbine_IN))
    OUT: Turbine_OUT = field(default=(Turbine_OUT))

@dataclass
class Turbine:
    HP: Turbine_Gen = field(default=Turbine_Gen)
    LP: Turbine_Gen = field(default=Turbine_Gen)

@dataclass
class Turbine_Stage_Info:
    degR_m: float
    power : float
    T0_1m : float
    T0_2m : float
    T0_3m : float
    P0_1m : float
    P0_2m : float
    P0_3m : float

####################################################
#                     Nozzle                       #
####################################################

@dataclass
class Nozzle_IN:
    m_dot_t         : float
    m_dot_b         : float
    T05             : float
    P05             : float
    T015            : float
    P015            : float
    T_a             : float
    P_a             : float
    gamma_n         : float
    gamma_fn        : float
    eta_n           : float
    eta_fn          : float

@dataclass
class Nozzle_OUT:
    exit_velocity_c:                  float
    exit_mach_c:                      float
    exit_area_c:                      float
    exit_velocity_b:                  float
    exit_mach_b:                      float
    exit_area_b:                      float

@dataclass
class Nozzle:
    IN:  Nozzle_IN = field(default=(Nozzle_IN))
    OUT: Nozzle_OUT = field(default=(Nozzle_OUT))

####################################################
#                    Pritchard                     #
####################################################
@dataclass
class pts:
    betas: list
    x_coords: list
    y_coords: list
    R_new = float
    Ct = int

@dataclass
class params:
    beta_IN: float
    beta_OUT: float
    ep_IN: float
    ep_OUT: float
    zeta: float
    Ct: float
    Cx: float
    N_B: float
    R: float
    R_TE: float

@dataclass 
class parameters:
    pitch: float
    t_max: float
    t_min: float
    R: float
    blockage_IN: float
    blockage_OUT: float
    zweifel: float
    chord: float
    calc_ttc: float

@dataclass
class blade:
    failcode: str
    x_comb: float
    y_comb: float
    x_thicc: float
    y_thicc: float
    
    x_pressure: float
    y_pressure: float
    ps_p1x: float
    ps_p1y: float
    k_max_ps: float
    x_suction: list
    y_suction: list
    x_spline_pts: list
    y_spline_pts: list
    k_max_ss: list
    norm_x: list
    norm_y: list
    suction_curvature: list

    x_o: list
    y_o: list
    x_thicc: list
    y_thicc: list

    LEx: list
    LEy: list
    TEx: list
    TEy: list