import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass

from Reference import REF_AEQ
from Reference import REF_structs

def Turbine_Stage_Pitchline(initial, Mc_2m, Mw_3Rm, alpha_1m, schrodinkler, T0_1m, P0_1m, r_mean, ang_vel, gamma_t, R_t, Cp_t, m_dot_t, degR_m, current_power, target_power):
    # ======== INPUTS ======== 
    # initial       | Whether or not this function call is for the first turbine stage
    # Mc_2m         | Target stator exit Mach number
    # Mw_3Rm        | Target rotor exit relative Mach number
    # alpha_1m      | Stator inlet angle
    # schrodinkler  | LE SCHRODINKLER: If first turbine stage, specify stator nozzle exit angle. If NOT first turbine stage, specify axial velocity z_3m of previous stage
    # T0_1m         | Stator inlet total temperature
    # P0_1m         | Stator inlet total pressure
    # r_mean        | Meanline radius
    # ang_vel       | Angular Velocity
    # gamma_t       | Specific heat ratio
    # R_t           | Gas constant R
    # Cp_t          | Specific heat at constant pressure for the turbine
    # m_dot_t       | Turbine mass flow rate
    # degR_m        | Stage degree of reaction
    # current_power | Power generation currently before adding on the present stage
    # target_power  | Power generation target
    
    # ======== Pitchline Calcs (turbine-specific station numbers) ========
    # Stator stuff
    T0_2m = T0_1m   # No total temp drop over stator, assume adiabatic
    T_2m = REF_AEQ.T_T0(gamma_t, Mc_2m)*T0_2m  
    a_2m = REF_AEQ.a(gamma_t, R_t, T_2m)

    C_2m = Mc_2m*a_2m
    
    if initial:
        alpha_2m = schrodinkler
        Ctheta_2m = C_2m*np.sin(alpha_2m)
        z_1m = z_2m = z_3m = C_2m*np.cos(alpha_2m)
    else:
        z_1m = z_2m = z_3m = schrodinkler
        alpha_2m = np.acos(z_2m/C_2m)
        Ctheta_2m = C_2m*np.sin(alpha_2m)

    C_1m = z_1m/np.cos(alpha_1m)
    Ctheta_1m = C_1m*np.sin(alpha_1m)

    T_1m = T0_1m - C_1m**2/(2*Cp_t)
    a_1m = REF_AEQ.a(gamma_t, R_t, T_1m)
    Mc_1m = C_1m/a_1m
    
    # Stator Solidity
    optimal_zweifel = 1
    fake_optimal_stator_solidity = REF_AEQ.sigXzweif(alpha_1m, alpha_2m) / optimal_zweifel
    Ctheta_mean = (Ctheta_1m + Ctheta_2m)/2
    alpha_2_stagger = np.atan(Ctheta_mean/z_2m)
    real_optimal_stator_solidity = fake_optimal_stator_solidity/np.cos(alpha_2_stagger)

    # Stator deviation angle and throat/spacing ratio
    if Mc_2m <= 1:
        stator_dev = (alpha_2m - alpha_1m) / (8 * real_optimal_stator_solidity)
        o_s = np.cos(alpha_2m)
    else:
        stator_dev = 0
        o_s = np.cos(alpha_2m) / REF_AEQ.A_Astar(gamma_t, Mc_2m)

    # ======== Have you tried spinning? It's a great trick ========
    # Calculating pitchline reference frame tangential velocity U
    U_1m = U_2m = U_3m = ang_vel * r_mean
    
    # Converting to rotating reference frame
    Wtheta_2m = Ctheta_2m - U_2m
    Wtheta_1m = Ctheta_1m - U_1m
    
    # Rotor exit relative and absolute tangential speed

    # This section below is for if we want to have degree of reaction be an ouput
    # Wtheta_3m = -np.sqrt( (Mw_3Rm**2*(a_2m**2+(gamma_t-1)*Wtheta_2m**2/2)-z_2m**2) / (1+(gamma_t-1)*Mw_3Rm**2/2) )
    # Ctheta_3m = U_2m + Wtheta_3m

    # This section below is for when we specify degree of reaction as a design variable
    Ctheta_3m = (1 - degR_m)*2*U_2m - Ctheta_2m
    Wtheta_3m = Ctheta_3m-U_3m

    # Calculating miscellaneous velocities and angles
    # Pythagoreas
    W_2m = np.sqrt(z_2m**2 + Wtheta_2m**2)
    W_3m = np.sqrt(z_3m**2 + Wtheta_3m**2)
    C_3m = np.sqrt(z_3m**2 + Ctheta_3m**2)
    W_1m = np.sqrt(z_1m**2 + Wtheta_1m**2)
    
    # Trig
    beta_1m = -np.acos(z_1m/W_1m)
    beta_2m = np.acos(z_2m/W_2m)
    beta_3m = -np.acos(z_3m/W_3m)
    alpha_3m = np.atan(Ctheta_3m/z_3m)

    # Miscellaneous temps n' stuff
    a_3m = W_3m/Mw_3Rm                  # Station 3 (rotor exit) speed of sound
    Mw_2m = W_2m/a_2m                   # Station 2 (rotor inlet) relative mach number
    Mw_1m = W_1m/a_1m                   # Station 1 (stator inlet) relative mach number
    T0_2Rm = T_2m + W_2m**2/(2*Cp_t)    # Station 2 (Rotor inlet) relative total temperature 

    Mz_1m = z_1m/a_1m                   # Station 1 axial mach number
    Mz_2m = z_2m/a_2m                   # Station 2 axial mach number
    Mz_3m = z_3m/a_3m                   # Station 3 axial mach number
    
    profileLoss_s = 0.06                # Assumed stator pressure loss coefficient
    
    # A lot of random temperatures and pressures, have fun reading through them lol
    P_1m = P0_1m * REF_AEQ.P_P0(gamma_t, Mc_1m)
    P0_2m = -profileLoss_s*(P0_1m - P_1m)+P0_1m
    P_2m = P0_2m * REF_AEQ.P_P0(gamma_t, Mc_2m)
    P0_2Rm = P_2m / REF_AEQ.P_P0(gamma_t, Mw_2m)
    T0_3m = T0_2m + U_2m*(Ctheta_3m-Ctheta_2m)/Cp_t
    T_3m = T0_3m - C_3m**2/(2*Cp_t)
    T0_3Rm = T_3m + W_3m**2/(2*Cp_t)
    a_3m = REF_AEQ.a(gamma_t, R_t, T_3m)
    Mc_3m = C_3m/a_3m
    
    profileLoss_r = 0.08                # Assumed rotor pressure loss coefficient
    P0_3Rm = -profileLoss_r*(P0_2Rm - P_2m)+P0_2Rm
    P_3m = P0_3Rm * REF_AEQ.P_P0(gamma_t, Mw_3Rm)
    P0_3m = P_3m / REF_AEQ.P_P0(gamma_t, Mc_3m)
    
    # Rotor solidity
    optimal_zweifel = 1
    fake_optimal_rotor_solidity = REF_AEQ.sigXzweif(beta_2m, beta_3m) / optimal_zweifel     # "Optimal" solidity based on Zweifel
    Wtheta_mean = (Wtheta_2m + Wtheta_3m)/2                                             # Average relative swirl
    beta_stagger = np.atan(Wtheta_mean/z_3m)                                            # Stagger angle
    real_optimal_stator_solidity = fake_optimal_rotor_solidity/np.cos(beta_stagger)     # Actual optimal solidity

    # Rotor deviation angle
    rotor_dev = (beta_3m - beta_2m)/(8*real_optimal_stator_solidity)                    # Rotor blade deviatino angle
    
    # Power
    w_spec = U_2m*(Ctheta_2m-Ctheta_3m)     # Euler's
    power = w_spec * m_dot_t                # Calculating stage power generation

    last = False
    if power + current_power > target_power:
        last = True

    # degR_m = 1 - (Ctheta_2m + Ctheta_3m)/(2*U_2m)     # Stage degree of reaction

    # ======== OUTPUT ========
    velocityTriangle = REF_structs.FullVelTriInfo(
        C_1m, C_2m, C_3m,
        W_1m, W_2m, W_3m,
        U_1m, U_2m, U_3m,
        z_1m, z_2m, z_3m,
                                       
        Mc_1m, Mc_2m, Mc_3m,
        Mw_1m, Mw_2m, Mw_3Rm,
        Mz_1m, Mz_2m, Mz_3m,
                                       
        Ctheta_1m, Ctheta_2m, Ctheta_3m,
        Wtheta_1m, Wtheta_2m, Wtheta_3m,
                                       
        alpha_1m, alpha_2m, alpha_3m,
        beta_1m,  beta_2m,  beta_3m
        )
    
    turbineStageInfo = REF_structs.Turbine_Stage_Info(
        degR_m,
        power,
        T0_1m,
        T0_2m,
        T0_3m,
        P0_1m,
        P0_2m,
        P0_3m
    )

    return [velocityTriangle, turbineStageInfo, last]

def Turbine_Annulus_Sizing(triangles, info, m_dot_target, gamma, R, r_mean_vec):
    # Setup for multi-stage shennanigans
    num_stages = len(info)
    num_stations = num_stages*2+1
    num_streamlines = 51 # how very odd (this number MUST be odd to ensure we actually have an integer middle index)

    # Calculations for initial annulus sizing without radial equilibrium effects
    r_hub_stations = [1 for _ in range(num_stations)]
    r_tip_stations = [1 for _ in range(num_stations)]
    rho_m_stations = [1 for _ in range(num_stations)]

    counter = 0
    for i in range(len(info)):
        r_hub_stations[counter], r_tip_stations[counter], rho_m_stations[counter] = annulus_adjust(
            info[i].T0_1m,
            info[i].P0_1m,
            R,
            gamma,
            m_dot_target,
            triangles[i].z_1m,
            triangles[i].Mc_1m,
            r_mean_vec[i]
        )
        r_hub_stations[counter+1], r_tip_stations[counter+1], rho_m_stations[counter+1] = annulus_adjust(
            info[i].T0_2m,
            info[i].P0_2m,
            R,
            gamma,
            m_dot_target,
            triangles[i].z_2m,
            triangles[i].Mc_2m,
            r_mean_vec[i]
        )
        counter = counter + 2
    r_hub_stations[num_stations-1], r_tip_stations[num_stations-1], rho_m_stations[num_stations-1] = annulus_adjust(info[-1].T0_3m, info[-1].P0_3m, R, gamma, m_dot_target, triangles[-1].z_3m, triangles[-1].Mc_3m, r_mean_vec[-1])


    stations = [_ for _ in range(1, num_stations+1)]

    # Plotting the hub and tip radii
    plt.plot(stations, r_tip_stations, 'k')
    plt.plot(stations, r_hub_stations, 'k')

    # Plotting the meanline
    r_mean_plot_stages =   [_*2 + 1 for _ in range(0, num_stages)]
    r_mean_plot_stages.append(r_mean_plot_stages[-1]+2)
    r_mean_vec_plot = r_mean_vec
    r_mean_vec_plot.append(r_mean_vec[-1])
    plt.plot(r_mean_plot_stages, r_mean_vec_plot, "--r")

    # Plotting the horizontal inlet radius line (to make the real meanline easier to see)
    plt.hlines(r_mean_vec[0], 1, stations[-1], linestyles='--', colors='gray')

    # Mirrored
    plt.plot(stations, [-_ for _ in r_tip_stations], 'k')
    plt.plot(stations, [-_ for _ in r_hub_stations], 'k')
    plt.plot(r_mean_plot_stages, [-_ for _ in r_mean_vec_plot], "--r")
    plt.hlines(-r_mean_vec[0], 1, stations[-1], linestyles='--', colors='gray')

    # print(rho_m_stations)
    


    ## ======== Vector Creation and Initialization ========
    r_spans      = [[] for _ in range(num_stations)]
    Ctheta_spans = [[] for _ in range(num_stations)]
    z_spans      = [[] for _ in range(num_stations)]
    rho_spans    = [[] for _ in range(num_stations)]
    T_spans      = [[] for _ in range(num_stations)]
    r_spans      = [[] for _ in range(num_stations)]

    # for i in range(len())

def annulus_adjust(T0, P0, R, gamma, m_dot, z, Mc, r_mean):
        T = T0 * REF_AEQ.T_T0(gamma, Mc) # | spanwise constant (design choice i think)
        P = P0 * REF_AEQ.P_P0(gamma, Mc) # | spanwise constant (design choice i think)
        rho_m = P/(R*T)

        A = m_dot/(rho_m*z)
        h = A / (4 * np.pi * r_mean)

        r_hub = r_mean - h
        r_tip = r_mean + h
    
        return [r_hub, r_tip, rho_m]

def pitchline_staging(initial, Mc_2m, Mw_3Rm, Mc_2m_default, Mw_3Rm_default, alpha_1m, alpha_2m, T0_4m, P0_4m, r_mean_i, ang_vel, gamma_t, R_t, Cp_t, m_dot_t, degR_m, req_power_t, **kwargs):
        # ======== Pitchline Staging ========
    # Setting up lists to contain staging data
    multistage_velocity_triangles = []
    multistage_info = []

    if initial:
        r_mean_vec = [r_mean_i for _ in range(0,50)] # kind of scuffed and is definitely not rigorous coding, but also, if it's telling us we need more than 50 turbine stages, we have bigger issues to worry about lol
    else:
        dr = kwargs["r_inc_factor"] * r_mean_i
        r_mean_vec = [r_mean_i + _*dr for _ in [_ for _ in range(0, kwargs["num_stages_target"])]]



    # First stage
    velocity_triangles_s1, info_s1, powerReqMet = Turbine_Stage_Pitchline(
        True,       # Initial
        Mc_2m,      
        Mw_3Rm,
        alpha_1m,
        alpha_2m,
        T0_4m,
        P0_4m,
        r_mean_vec[0],
        ang_vel,
        gamma_t,
        R_t,
        Cp_t,
        m_dot_t,
        degR_m,
        0,          # Current_Power
        req_power_t
        )
    multistage_velocity_triangles.append(velocity_triangles_s1)
    multistage_info.append(info_s1)
    
    total_power_generated = multistage_info[0].power

    # Subsequent staging for initial case:
    if initial:
        stage_idx = 1
        while not powerReqMet:  # FOR INITIAL CASE: Continues generating stages until power generates exceeds required power
            # Calculate triangles and info for new stage
            velocity_triangles, info, powerReqMet = Turbine_Stage_Pitchline(
                False,
                Mc_2m_default,
                Mw_3Rm_default,
                multistage_velocity_triangles[stage_idx-1].alpha_3m,
                multistage_velocity_triangles[stage_idx-1].z_3m,
                multistage_info[stage_idx-1].T0_3m,
                multistage_info[stage_idx-1].P0_3m,
                r_mean_vec[stage_idx],
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
    else:
        stage_idx = 1
        for _ in range(kwargs["num_stages_target"]-1):  # FOR SUBSEQUENT PASSES: Generates the specified number of stages, then stops, regardless of whether or not power requirement is met
            # Calculate triangles and info for new stage
            velocity_triangles, info, powerReqMet = Turbine_Stage_Pitchline(
                False,
                Mc_2m_default,
                Mw_3Rm_default,
                multistage_velocity_triangles[stage_idx-1].alpha_3m,
                multistage_velocity_triangles[stage_idx-1].z_3m,
                multistage_info[stage_idx-1].T0_3m,
                multistage_info[stage_idx-1].P0_3m,
                r_mean_vec[stage_idx],
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

    num_stages = len(multistage_velocity_triangles)
    num_stages_target = num_stages - 1      # This will calculate a number for non-initial passes, but is meaningless unless it is the initial pass

    total_power_generated = sum([info.power for info in multistage_info])
    excess_power_margin = (total_power_generated - req_power_t)/req_power_t * 100

    if initial:
        r_mean_vec = [r_mean_i for _ in range(0, num_stages)]

    return REF_structs.Turbine_Pitchline_Results(multistage_velocity_triangles, multistage_info, r_mean_vec, total_power_generated, excess_power_margin, num_stages_target)