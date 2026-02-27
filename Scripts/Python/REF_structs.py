from dataclasses import dataclass

@dataclass
class ByComponent:
    a:   float      # Ambient
    d:   float      # Diffuser
    f:   float      # Fan
    fn:  float      # Fan Nozzle
    cLP: float      # LP Compressor
    cHP: float      # HP Compressor
    b:   float      # Burner
    tHP: float      # HP Turbine
    tLP: float      # LP Turbine
    n:   float      # Nozzle

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
class fullVelTriInfo:
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
