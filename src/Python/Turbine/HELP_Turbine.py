import numpy as np
import matplotlib.pyplot as plt

from Reference import REF_AEQ
from Reference import REF_structs

def Turbine_Stage_Pitchline(initial, Mc_2m, Mw_3Rm, alpha_1m, schrodinkler, T0_1m, P0_1m, r_mean, ang_vel, gamma_t, R_t, Cp_t, m_dot_t, current_power, target_power):
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
    # current_power | Power generation currently before adding on the present stage
    # target_power  | Power generation target
    
    # ======== Pitchline Calcs (turbine-specific station numbers) ========
    T0_2m = T0_1m   # No total temp drop over stator
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
    Wtheta_3m = -np.sqrt( (Mw_3Rm**2*(a_2m**2+(gamma_t-1)*Wtheta_2m**2/2)-z_2m**2) / (1+(gamma_t-1)*Mw_3Rm**2/2) )
    Ctheta_3m = U_2m + Wtheta_3m

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

    degR_m = 1 - (Ctheta_2m + Ctheta_3m)/(2*U_2m)     # Stage degree of reaction

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

def Turbine_Annulus_Sizing(triangles, info, m_dot_target, gamma, R, r_mean_1):
    # Setup for multi-stage shennanigans
    num_stages = len(info)
    num_stations = num_stages*2+1
    num_streamlines = 51 # how very odd (this number MUST be odd to ensure we actually have an integer middle index)

    # Calculations for initial annulus sizing without radial equilibrium effects
    r_hub_stations = [1 for _ in range(num_stations)]
    r_tip_stations = [1 for _ in range(num_stations)]
    rho_m_stations = [1 for _ in range(num_stations)]

    r_hub_stations[0], r_tip_stations[0], rho_m_stations[0] = annulus_adjust(info[0].T0_1m, info[0].P0_1m, R, gamma, m_dot_target, triangles[0].z_1m, triangles[0].Mc_1m, r_mean_1)
    counter = 1
    for i in range(len(info)):
        r_hub_stations[counter], r_tip_stations[counter], rho_m_stations[counter] = annulus_adjust(
            info[i].T0_2m,
            info[i].P0_2m,
            R,
            gamma,
            m_dot_target,
            triangles[i].z_2m,
            triangles[i].Mc_2m,
            r_mean_1
        )
        r_hub_stations[counter+1], r_tip_stations[counter+1], rho_m_stations[counter+1] = annulus_adjust(
            info[i].T0_3m,
            info[i].P0_3m,
            R,
            gamma,
            m_dot_target,
            triangles[i].z_3m,
            triangles[i].Mc_3m,
            r_mean_1
        )
        counter = counter + 2
    stations = [_ for _ in range(1, num_stations+1)]
    plt.plot(stations, r_tip_stations)
    plt.plot(stations, r_hub_stations)

    plt.plot(stations, [-_ for _ in r_tip_stations])
    plt.plot(stations, [-_ for _ in r_hub_stations])

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