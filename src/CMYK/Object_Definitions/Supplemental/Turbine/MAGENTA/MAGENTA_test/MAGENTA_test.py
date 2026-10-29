from CoolProp.CoolProp import PropsSI
import MAGENTA as mag
import numpy as np


def MAGENTA():

    # ========== MAGENTA TEST VALUES ==========
    # Values taken from turbojet
    gamma   = 1.33 		            # estimate based on combustion products and temperature)
    Cp      = 1070		            # J/kg*K (estimate based on combustion products and temperature)
    R       = ((gamma-1)*Cp)/gamma  # J/kg*K
    m_dot   = 0.5                   # kg/s 
    T0_1m   = 1000                  # K
    P0_1m   = 3*101325              # Pa
    req_power = 100*745.7           # W
    rpm     = 80000                    

    # Design decisions taken from turbofan inputs
    r_mean_i = 0.075
    # First stage design decisions
    alpha_1m        = 0.0
    alpha_2m        = 60 * (np.pi/180)  # radians
    Mc_2m            = 1.1
    Mw_3Rm        = 0.8

    # Multistage design decisions
    Mc_2m_default   = 0.964
    Mw_3Rm_default  = 0.85
    degR_m          = 0.5
    # =========================================

    ang_vel = rpm * 2*np.pi / 60 # Angular velocity, rad/s

    # ======== Pitchline Staging ========
    # Setting up lists to contain staging data

    initial_pitchline_res = mag.pitchline_staging(
        True,   # initial
        Mc_2m,
        Mw_3Rm,
        Mc_2m_default,
        Mw_3Rm_default,
        alpha_1m,
        alpha_2m,
        T0_1m,
        P0_1m,
        r_mean_i,
        ang_vel,
        gamma,
        R,
        Cp,
        m_dot,
        degR_m,
        req_power
    )

    num_stages_target = initial_pitchline_res.num_stages_target

    total_power_generated = 0
    r_inc_factor = 0

    if num_stages_target > 1:
        while total_power_generated < req_power:
            pitchline_res = mag.pitchline_staging(
                False,   # initial
                Mc_2m,
                Mw_3Rm,
                Mc_2m_default,
                Mw_3Rm_default,
                alpha_1m,
                alpha_2m,
                T0_1m,
                P0_1m,
                r_mean_i,
                ang_vel,
                gamma,
                R,
                Cp,
                m_dot,
                degR_m,
                req_power,
                r_inc_factor = r_inc_factor,
                num_stages_target = num_stages_target
            )
            total_power_generated = pitchline_res.total_power_generated
            r_mean_i += 0.01
            r_inc_factor += 0.01
    else:
        percent_error = 5
        while percent_error > 2 or percent_error < 0:
            pitchline_res = mag.pitchline_staging(
                False,   # initial
                Mc_2m,
                Mw_3Rm,
                Mc_2m_default,
                Mw_3Rm_default,
                alpha_1m,
                alpha_2m,
                T0_1m,
                P0_1m,
                r_mean_i,
                ang_vel,
                gamma,
                R,
                Cp,
                m_dot,
                degR_m,
                req_power,
                r_inc_factor = r_inc_factor,
                num_stages_target = num_stages_target
            )
            total_power_generated = pitchline_res.total_power_generated
            percent_error = (total_power_generated-req_power)/req_power * 100
            if percent_error < 0:
                degR_m += 0.005
            else:
                degR_m -= 0.005

    #self.pitchline_res = pitchline_res

    mag.Turbine_Annulus_Sizing(
        pitchline_res.multistage_velocity_triangles,
        pitchline_res.multistage_info,
        m_dot,
        gamma,
        R,
        pitchline_res.r_mean_vec
    )

    print('Done :)')

    return
