from Object_Definitions.Base_Objects import Flow, VelocityTriangle
import Turbine_REF_structs
from Run import helper_functions as hf
import numpy as np
import matplotlib.pyplot as plt

# HELPER FUNCTIONS
def Turbine_Stage_Pitchline(initial, Mc_2m, Mw_3Rm, alpha_1m, schrodinkler, T0_1m, P0_1m, r_mean, ang_vel, gamma_t, R_t, Cp_t, m_dot_t, degR_m, current_power, target_power):
    """
    Calculate one turbine stage at the meanline.

    All flow angles are in radians.

    If initial:
        schrodinkler is the specified stator exit angle alpha_2m.

    Otherwise:
        schrodinkler is the axial velocity z_3m from the
        preceding stage, which becomes this stage's inlet
        and stator-exit axial velocity.

    degR_m is prescribed. Consequently, the actual rotor
    exit relative Mach number is calculated rather than
    forced to equal Mw_3Rm.
    """
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

    # -----------------------------------------------------
    #                  INPUT VALIDATION
    # -----------------------------------------------------

    values = np.asarray([
        Mc_2m, Mw_3Rm, alpha_1m, schrodinkler,
        T0_1m, P0_1m, r_mean, ang_vel,
        gamma_t, R_t, Cp_t, m_dot_t,
        degR_m, current_power, target_power
    ], dtype=float)

    if not np.all(np.isfinite(values)):
        raise ValueError("Non-finite input to Turbine_Stage_Pitchline.")

    if Mc_2m <= 0 or Mw_3Rm <= 0:
        raise ValueError("Mach numbers must be positive.")

    if T0_1m <= 0 or P0_1m <= 0:
        raise ValueError("Inlet total temperature and pressure must be positive.")

    if r_mean <= 0 or m_dot_t <= 0:
        raise ValueError("Mean radius and mass flow must be positive.")

    if gamma_t <= 1 or R_t <= 0 or Cp_t <= 0:
        raise ValueError("Invalid gas properties.")

    if target_power <= 0:
        raise ValueError("Target turbine power must be positive.")

    # -----------------------------------------------------
    #                  STATOR CALCULATIONS
    # -----------------------------------------------------

    T0_2m = T0_1m

    T_2m = T0_2m * hf.T_T0(gamma_t, Mc_2m)
    a_2m = hf.a(gamma_t, R_t, T_2m)

    C_2m = Mc_2m * a_2m

    if initial:
        # First-stage stator exit angle is prescribed.
        alpha_2m = float(schrodinkler)
        z_2m = C_2m * np.cos(alpha_2m)
        Ctheta_2m = C_2m * np.sin(alpha_2m)
    else:
        # Subsequent-stage axial velocity is inherited from the preceding stage
        z_2m = float(schrodinkler)

        if z_2m <= 0 or z_2m > C_2m:
            raise ValueError("Infeasible axial velocity for the specified stator exit Mach.")

        Ctheta_2m = np.sqrt(max(C_2m**2 - z_2m**2, 0.0))
        alpha_2m = np.arctan2(Ctheta_2m, z_2m)

    if z_2m <= 0:
        raise ValueError("Calculated axial velocity must be positive.")

    # Constant axial velocity through this stage, matching the existing design assumption.

    z_1m = z_2m
    z_3m = z_2m

    # Stator inlet velocity.
    cos_alpha_1m = np.cos(alpha_1m)
    if cos_alpha_1m <= 0:
        raise ValueError("Invalid stator inlet flow angle.")

    C_1m = z_1m / cos_alpha_1m
    Ctheta_1m = C_1m * np.sin(alpha_1m)

    T_1m = T0_1m - C_1m**2 / (2.0 * Cp_t)
    if T_1m <= 0:
        raise ValueError("Calculated stator inlet static temperature is nonpositive.")

    a_1m = hf.a(gamma_t, R_t, T_1m)
    Mc_1m = C_1m / a_1m

    # -----------------------------------------------------
    #                  ROTOR CALCULATIONS
    # -----------------------------------------------------
    # Meanline blade speed. The existing model assumes a constant mean radius throughout each stage.
    U_1m = U_2m = U_3m = ang_vel * r_mean

    Wtheta_1m = Ctheta_1m - U_1m
    Wtheta_2m = Ctheta_2m - U_2m

    # Degree of reaction determines rotor exit swirl.
    Ctheta_3m = (2.0 * (1.0 - degR_m) * U_2m - Ctheta_2m)

    Wtheta_3m = Ctheta_3m - U_3m

    # Absolute and relative velocity magnitudes.
    C_3m = np.hypot(z_3m, Ctheta_3m)

    W_1m = np.hypot(z_1m, Wtheta_1m)
    W_2m = np.hypot(z_2m, Wtheta_2m)
    W_3m = np.hypot(z_3m, Wtheta_3m)

    # -----------------------------------------------------
    #                  VELOCITY ANGLES
    # -----------------------------------------------------
    # Use arctan2 to preserve the correct signs and quadrants.
    beta_1m = np.arctan2(Wtheta_1m, z_1m)
    beta_2m = np.arctan2(Wtheta_2m, z_2m)
    beta_3m = np.arctan2(Wtheta_3m, z_3m)

    alpha_3m = np.arctan2(Ctheta_3m, z_3m)

    # -----------------------------------------------------
    #                  TEMPERATURES
    # -----------------------------------------------------

    # Euler turbine work equation.
    T0_3m = (T0_2m + U_2m * (Ctheta_3m - Ctheta_2m) / Cp_t)

    T_3m = T0_3m - C_3m**2 / (2.0 * Cp_t)
    if T0_3m <= 0 or T_3m <= 0:
        raise ValueError("Calculated rotor exit temperature is nonpositive.")

    a_3m = hf.a(gamma_t, R_t, T_3m)

    # -----------------------------------------------------
    #                  MACH NUMBERS
    # -----------------------------------------------------

    # Relative and absolute rotor exit Mach numbers
    # must be calculated from the same physical state.

    Mc_2m_actual = Mc_2m
    Mc_3m = C_3m / a_3m

    Mw_1m = W_1m / a_1m
    Mw_2m = W_2m / a_2m
    Mw_3m_actual = W_3m / a_3m

    Mz_1m = z_1m / a_1m
    Mz_2m = z_2m / a_2m
    Mz_3m = z_3m / a_3m

    # -----------------------------------------------------
    #                  PRESSURE CALCULATIONS
    # -----------------------------------------------------

    # Stator pressure loss.
    profileLoss_s = 0.06

    P_1m = P0_1m * hf.P_P0(gamma_t, Mc_1m)

    P0_2m = (P0_1m - profileLoss_s * (P0_1m - P_1m))
    P_2m = P0_2m * hf.P_P0(gamma_t, Mc_2m)

    # Rotor inlet relative total pressure.
    P0_2Rm = P_2m / hf.P_P0(gamma_t, Mw_2m)

    # Rotor pressure loss.
    profileLoss_r = 0.08

    P0_3Rm = (P0_2Rm - profileLoss_r * (P0_2Rm - P_2m))

    # Use the ACTUAL rotor exit relative Mach number.
    # Mw_3Rm is a target input, but degree of reaction is the active design variable in this formulation.
    P_3m = P0_3Rm * hf.P_P0(gamma_t, Mw_3m_actual)

    # Convert back to absolute total pressure.
    P0_3m = P_3m / hf.P_P0(gamma_t, Mc_3m)

    if min(P0_2m, P_2m, P0_2Rm, P0_3Rm, P_3m, P0_3m) <= 0:
        raise ValueError("Calculated turbine pressure is nonpositive.")

    # -----------------------------------------------------
    #                  POWER CALCULATION
    # -----------------------------------------------------
    w_spec = U_2m * (Ctheta_2m - Ctheta_3m)

    power = w_spec * m_dot_t
    if power <= 0:
        raise ValueError("Calculated turbine stage power is nonpositive. ", "Check reaction, velocity angles and rotation direction.")

    last = (current_power + power >= target_power)

    # -----------------------------------------------------
    #                  OUTPUT STRUCTURES
    # -----------------------------------------------------

    velocityTriangle = Turbine_REF_structs.FullVelTriInfo(
        C_1m, C_2m, C_3m,
        W_1m, W_2m, W_3m,
        U_1m, U_2m, U_3m,
        z_1m, z_2m, z_3m,

        Mc_1m, Mc_2m_actual, Mc_3m,
        Mw_1m, Mw_2m, Mw_3m_actual,
        Mz_1m, Mz_2m, Mz_3m,

        Ctheta_1m, Ctheta_2m, Ctheta_3m,
        Wtheta_1m, Wtheta_2m, Wtheta_3m,

        alpha_1m, alpha_2m, alpha_3m,
        beta_1m, beta_2m, beta_3m
    )

    turbineStageInfo = Turbine_REF_structs.Turbine_Stage_Info(
        degR_m,
        power,
        T0_1m,
        T0_2m,
        T0_3m,
        P0_1m,
        P0_2m,
        P0_3m
    )

    return velocityTriangle, turbineStageInfo, last


def Turbine_Annulus_Sizing(triangles,info,m_dot_target,gamma,R, r_mean_vec, num_streamlines=51):
    """
    Calculate the initial annulus geometry at all three
    stations of every turbine stage.

    Each stage has:
        1m: Stator inlet
        2m: Stator exit / rotor inlet
        3m: Rotor exit

    Three stations are retained per stage so that
    stage-to-stage mean-radius changes are represented.

    This calculates initial annulus geometry only.
    """

    # -----------------------------------------------------
    #                  INPUT VALIDATION
    # -----------------------------------------------------

    num_stages = len(info)

    if num_stages < 1:
        raise ValueError("No turbine stages supplied.")

    if len(triangles) != num_stages:
        raise ValueError("Velocity triangle count does not match stage count.")

    r_mean_vec = np.asarray(r_mean_vec, dtype=float)

    if len(r_mean_vec) != num_stages:
        raise ValueError("Mean radius vector does not match stage count.")

    if not np.all(np.isfinite(r_mean_vec)) or np.any(r_mean_vec <= 0):
        raise ValueError("Mean radii must be finite and positive.")

    if not isinstance(num_streamlines, (int, np.integer)):
        raise TypeError("num_streamlines must be an integer.")

    if num_streamlines < 3 or num_streamlines % 2 == 0:
        raise ValueError(
            "num_streamlines must be an odd integer of at least 3."
        )

    # -----------------------------------------------------
    #                  STATION SETUP
    # -----------------------------------------------------

    num_stations = 3 * num_stages

    r_hub_stations = np.empty(num_stations)
    r_tip_stations = np.empty(num_stations)
    rho_m_stations = np.empty(num_stations)
    r_mean_stations = np.empty(num_stations)

    stage_station_indices = []

    # -----------------------------------------------------
    #               ANNULUS SIZING
    # -----------------------------------------------------

    for i in range(num_stages):

        # The three stations belonging to this stage.

        stage_stations = [
            (info[i].T0_1m, info[i].P0_1m, triangles[i].z_1m, triangles[i].Mc_1m),
            (info[i].T0_2m, info[i].P0_2m, triangles[i].z_2m, triangles[i].Mc_2m),
            (info[i].T0_3m, info[i].P0_3m, triangles[i].z_3m, triangles[i].Mc_3m)
        ]

        # Mean radius used for this stage.
        r_mean = r_mean_vec[i]

        first_station = 3 * i

        # Calculate all three annulus stations.
        for j, station_data in enumerate(stage_stations):
            T0, P0, z, Mc = station_data
            station_index = first_station + j

            (r_hub_stations[station_index], r_tip_stations[station_index], rho_m_stations[station_index]
             ) = annulus_adjust(T0, P0, R, gamma, m_dot_target, z, Mc, r_mean)

            r_mean_stations[station_index] = r_mean

        # Save the indices for later use in YELLOW.
        stage_station_indices.append({"inlet": first_station, "stator_exit": first_station + 1, "rotor_exit": first_station + 2})

    # -----------------------------------------------------
    #                GEOMETRY VALIDATION
    # -----------------------------------------------------
    if not (np.all(np.isfinite(r_hub_stations)) and np.all(np.isfinite(r_tip_stations)) and np.all(np.isfinite(rho_m_stations))):
        raise RuntimeError("Non-finite annulus sizing result.")

    if np.any(r_hub_stations <= 0):
        raise RuntimeError("A calculated hub radius is nonpositive.")

    if np.any(r_tip_stations <= r_hub_stations):
        raise RuntimeError("Invalid hub/tip radius relationship.")

    if np.any(rho_m_stations <= 0):
        raise RuntimeError("Calculated density must be positive.")

    r_spans = [np.linspace(r_hub_stations[i], r_tip_stations[i], num_streamlines) for i in range(num_stations)]

    return {
        "r_hub": r_hub_stations,
        "r_tip": r_tip_stations,
        "r_mean": r_mean_stations,
        "rho_mean": rho_m_stations,
        "r_spans": r_spans,
        "stage_station_indices": stage_station_indices,
        "num_stages": num_stages,
        "num_stations": num_stations,
        "num_streamlines": num_streamlines
    }


def annulus_adjust(T0, P0, R, gamma, m_dot, z, Mc, r_mean):
        T = T0 * hf.T_T0(gamma, Mc) # | spanwise constant (design choice i think)
        P = P0 * hf.P_P0(gamma, Mc) # | spanwise constant (design choice i think)
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
    # TODO: Verify if its actually num_stages
    num_stages_target = num_stages #- 1 if num_stages != 1 else 1      # This will calculate a number for non-initial passes, but is meaningless unless it is the initial pass

    total_power_generated = sum([info.power for info in multistage_info])
    excess_power_margin = (total_power_generated - req_power_t)/req_power_t * 100

    if initial:
        r_mean_vec = [r_mean_i for _ in range(0, num_stages)]

    return Turbine_REF_structs.Turbine_Pitchline_Results(multistage_velocity_triangles, multistage_info, r_mean_vec, total_power_generated, excess_power_margin, num_stages_target)