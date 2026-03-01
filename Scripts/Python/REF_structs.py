from dataclasses import dataclass, field

####################################################
#                      Cycle                       #
####################################################
@dataclass
class Cycle_IN:
    eta    : ByComponent = None
    gamma  : ByComponent = None
    Pr     : ByComponent = None
    T_0    : float = None
    P_0    : float = None
    M_f    : float = None
    Ra     : float = None
    Rp     : float = None
    QR     : float = None
    bypass : float = None
    combustion_temp: float = None

@dataclass
class Cycle_OUT:
    T0P0            : StationThermo = None
    Cps             : ByComponent = None
    ST              : float = None
    TSFC            : float = None
    total_thrust    : float = None
    core_thrust     : float = None
    bypass_thrust   : float = None
    eta_p           : float = None
    eta_th          : float = None
    eta_0           : float = None
    m_dot_core      : float = None
    m_dot_bypass    : float = None
    m_dot_total     : float = None
    u_ec            : float = None
    u_ef            : float = None

@dataclass
class ByComponent:
    a:   float = None     # Ambient
    d:   float = None      # Diffuser
    f:   float = None      # Fan
    fn:  float = None      # Fan Nozzle
    cLP: float = None      # LP Compressor
    cHP: float = None      # HP Compressor
    b:   float = None      # Burner
    tHP: float = None      # HP Turbine
    tLP: float = None      # LP Turbine
    n:   float = None      # Nozzle

@dataclass
class StationTnP:
    T0: float
    P0: float
    
@dataclass
class StationThermo:
    Sa:  StationTnP
    S15: StationTnP
    S2:  StationTnP
    S25: StationTnP
    S3:  StationTnP
    S4:  StationTnP
    S45: StationTnP
    S5:  StationTnP
    S6:  StationTnP
    S7:  StationTnP
    S8:  StationTnP

@dataclass
class Cycle:
    IN: Cycle_IN = field(default=Cycle_IN)
    OUT: Cycle_OUT = field(default=Cycle_OUT)

####################################################
#                    Compressor                    #
####################################################

@dataclass
class Compressor_IN:
    gamma           : float
    Cp_cLP          : float
    T0_1            : float
    P0_1            : float
    Pr              : float
    e_c             : float
    httrr           : float
    deHaller        : float
    min_Re          : float
    mu_kin          : float
    alpha_1m        : float
    Mz_1m           : float
    M_tip_inlet_max : float
    m_dot_core      : float

@dataclass
class Compressor_OUT:
    RVT                 : FullVelTriInfo = None
    FF                  : CompressorField = None
    P0_stages           : list = None
    T0_stages           : list = None
    r_hub_vec           : list = None
    r_tip_vec           : list = None
    Pr_stages           : list = None
    stage_info          : dict = None
    num_stages_actual   : float = None
    num_stages          : float = None
    RPM                 : float = None
    chord_m             : float = None
    Pr_total            : float = None
    Pr_total_actual     : float = None
    Tr_total            : float = None
    Tr_total_actual     : float = None
    P0_rise_total       : float = None
    temp_rise_total     : float = None
    temp_rise_per_stage : float = None
    U_tip_inlet         : float = None
    r_mean_1            : float = None


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
class CompressorField:
    Ctheta_spans:    list
    z_spans:         list
    rho_spans:       list
    T_spans:         list
    r_spans:         list
    r_hub_vec_full:  list
    r_tip_vec_full:  list
    rho_m_vec_full:  list
    degR_spans:      list
    num_stations:    list
    num_streamlines: list

@dataclass
class Compressor_Gen:
    IN: Compressor_IN = field(default=Compressor_IN)
    OUT: Compressor_OUT = field(default=Compressor_OUT)

@dataclass
class Compressor:
    LP:  Compressor_Gen = field(default=Compressor_Gen)
    HP: Compressor_Gen = field(default=Compressor_Gen)

####################################################
#                     Turbine                      #
####################################################

@dataclass
class Turbine_IN:
    m_dot_t         : float
    m_dot_c         : float
    RPM             : float

    T0_2comp        : float
    T0_3comp        : float
    T0_4m           : float
    P0_4m           : float

    r_mean_c        : float

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

@dataclass
class Turbine_OUT:
    multistage_velocity_triangles:  list
    multistage_info:                list
    total_power_gen:                float
    req_power:                      float
    req_power_comp:                 float
    req_power_fan:                  float
    excess_power_margin:            float

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

####################################################
#                     Turbofan                     #
####################################################

@dataclass
class TF:
    cycle:      Cycle = field(default=Cycle)
    compressor: Compressor = field(default=Compressor)
    turbine:    Turbine = field(default=Turbine)