from CoolProp.CoolProp import PropsSI
from CMYK.Object_Definitions.Base_Objects import Turbine
from Base_Objects import Flow, VelocityTriangle
from Run import helper_functions as hf 
from Supplemental.Turbine import MAGENTA as mag
import numpy as np
import math as m
import sympy
import AxialCompressor

class AxialTurbine(Turbine):

    def __init__(self, name):
        super().__init__(name, 'FLOWPATH')
        #-----------------------------------------------------
        #            Flow Flow Inlets and Exits
        #-----------------------------------------------------
        self.FlowIn = None
        self.FlowOut = None

        #-----------------------------------------------------
        #          Inlet and Exit Geometry Interfaces
        #-----------------------------------------------------
        self.GeoIn = None
        self.GeoOut = None

        #-----------------------------------------------------
        #                    SHAFT OUTPUT
        #-----------------------------------------------------
        self.Shaft = None

        # COMPONENT PARAMETERS -------------------------------
        self.eta = None

        self.Wfactor = None
        self.Wstream = None

    def config(self) -> None:
        cfg = self.cfg[self.name]
        self.Wstream = cfg['Wstream']

        self.eta = cfg['eta']

        # MAGENTA Config ---------------
        self.alpha_1m        = np.radians(cfg['alpha_1m'])
        self.alpha_2m        = np.radians(cfg['alpha_2m'])
        self.Mc_2m           = cfg['Mc_2m']
        self.Mw_3Rm          = cfg['Mw_3Rm']                    
        self.Mc_2m_default   = cfg['Mc_2m_default']             
        self.Mw_3Rm_default  = cfg['Mw_3Rm_default']             
        self.degR_m          = cfg['degR_m']

    #-----------------------------------------------------
    #                   CMYK Methods
    #-----------------------------------------------------

    def CYAN(self) -> None:
        # PREPARING REQUIRED VALUES ---------------------
        self.Wfactor = Wfactor = self.FlowIn.Wfactor
        eta = self.eta
        eta_mech = self.Shaft.eta_mech
        h01 = self.FlowIn.h0
        s1 = self.FlowIn.s
        # POWER BALANCE ----------------------------------
        self.Shaft.calc_consumer_specific_required_power()
        specific_req_power = self.Shaft.specific_required_power

        h02 = specific_req_power/(-Wfactor*eta_mech) + h01
        h02s = (h02-h01)/eta + h01
        s2s = s1

        P02s = PropsSI('P', 'HMASS', h02s, 'S', s2s, self.FlowIn.WF)
        P02 = P02s
        T02 = PropsSI('T', 'HMASS', h02, 'P', P02, self.FlowIn.WF)

        # SET EXIT FLOW ----------------------------------
        self.FlowOut.setFlow(
            T0=T02, P0=P02, FAR = self.FlowIn.FAR,
            Wfactor=self.Wfactor, Wstream=self.Wstream
        )

    def MAGENTA(self) -> None:
        '''
        Notes/TODO
        - For power matching, the final decision as to whether we increase meanline radius for all stages at once, linearly per stage, or both, is still to be decided.
        Right now it does both, leading to the kind of wacky geometry that is output.
        - Might want to consider using an iterative approach to switch to having a constant hub radius model for the annulus geometry
        - Finish annulus sizing/spanwise analysis of the turbine by implementing radial equilibrium.
        '''

        gamma   = self.FlowIn.gamma0
        Cp      = self.FlowIn.Cp0
        R       = self.FlowIn.R
        T0_1m   = self.FlowIn.T0        # Turbine inlet total temperature, K
        P0_1m   = self.FlowIn.P0        # Turbine inlet total pressure,    Pa 
        m_dot   = self.FlowIn.W         # Turbine total mass flow, kg/s, air plus fuel

        req_power = self.Shaft.required_power

        # First stage design decisions
        alpha_1m        = self.alpha_1m
        alpha_2m        = self.alpha_2m
        Mc_2m           = self.Mc_2m                      # Slightly supersonic stator nozzle exit
        Mw_3Rm          = self.Mw_3Rm                     # TODO find justification for this

        # Multistage design decisions
        Mc_2m_default   = self.Mc_2m_default              # Just barely not choking the flow at stator nozzle exit
        Mw_3Rm_default  = self.Mw_3Rm_default             # TODO find justification for this
        degR_m          = self.degR_m

        # ================= OLD CODE VARIABLE INPUTS =================

        rpm             = params.RPM        # RPM          TODO get rpm/ang_vel from HPC

        r_mean_i        = params.r_mean_i   # Inlet pitchline radius, meters    TODO get new formulation for r_mean_i (originally comes from LPC)

        m_dot_cool      = params.m_dot_cool # Cooling air bleedoff mass flow, kg/s
        T0_cool         = params.T0_cool    # Cooling air temperature, kelvin
        P0_cool         = params.P0_cool    # Cooling air pressure, Pa

        ep              = params.ep

        # ================= END OLD CODE VARIABLE INPUTS =================
        
        ang_vel = rpm * 2*np.pi / 60 # Angular velocity, rad/s

        # Old code power calculations :
        # removed since power is now calculated by shaft
        #
        # ======== Whole Turbine Calcs (absolute station numbers) ========
        #power_c = m_dot_c * Cp_c * (T0_3-T0_2)          # Power required by compressor          | TODO get exact power equation, this is just an approximation
        #power_f = 0 if m_dot_f == None else m_dot_f * Cp_f * (T0_2-T0_15)
        #req_power_t = power_c + power_f/eta_mech                          # Turbine power generation requirement  | Accounts for mechanical losses

        # Old code something, not used at all later so commented out for now :
        #
        # Using symbolic equations to solve for the exit temperature of the whole turbine
        #T0_5_cooled_sym = sympy.symbols("T0_5_cooled_sym")                                                                  # Creating symbolic variable
        #eqn1 = sympy.Eq(m_dot_c * ((1-ep)*Cp_t*(T0_1m-T0_5_cooled_sym) + ep*Cp_c*(T0_cool-T0_5_cooled_sym)), req_power)     # Defining equation
        #T0_5m_cooled = sympy.solve(eqn1, T0_5_cooled_sym)[0]                                                                # Solving
        # Total temperature drop across entire turbine
        #deltaT_total = T0_1m - T0_5m_cooled


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

        mag.Turbine_Annulus_Sizing(
            pitchline_res.multistage_velocity_triangles,
            pitchline_res.multistage_info,
            m_dot,
            gamma,
            R,
            pitchline_res.r_mean_vec
        )

        return




    # HELPER FUNCTIONS
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
        T_2m = hf.T_T0(gamma_t, Mc_2m)*T0_2m  
        a_2m = hf.a(gamma_t, R_t, T_2m)

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
        a_1m = hf.a(gamma_t, R_t, T_1m)
        Mc_1m = C_1m/a_1m
        
        # Stator Solidity
        optimal_zweifel = 1
        fake_optimal_stator_solidity = hf.sigXzweif(alpha_1m, alpha_2m) / optimal_zweifel
        Ctheta_mean = (Ctheta_1m + Ctheta_2m)/2
        alpha_2_stagger = np.atan(Ctheta_mean/z_2m)
        real_optimal_stator_solidity = fake_optimal_stator_solidity/np.cos(alpha_2_stagger)

        # Stator deviation angle and throat/spacing ratio
        if Mc_2m <= 1:
            stator_dev = (alpha_2m - alpha_1m) / (8 * real_optimal_stator_solidity)
            o_s = np.cos(alpha_2m)
        else:
            stator_dev = 0
            o_s = np.cos(alpha_2m) / hf.A_Astar(gamma_t, Mc_2m)

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
        P_1m = P0_1m * hf.P_P0(gamma_t, Mc_1m)
        P0_2m = -profileLoss_s*(P0_1m - P_1m)+P0_1m
        P_2m = P0_2m * hf.P_P0(gamma_t, Mc_2m)
        P0_2Rm = P_2m / hf.P_P0(gamma_t, Mw_2m)
        T0_3m = T0_2m + U_2m*(Ctheta_3m-Ctheta_2m)/Cp_t
        T_3m = T0_3m - C_3m**2/(2*Cp_t)
        T0_3Rm = T_3m + W_3m**2/(2*Cp_t)
        a_3m = hf.a(gamma_t, R_t, T_3m)
        Mc_3m = C_3m/a_3m
        
        profileLoss_r = 0.08                # Assumed rotor pressure loss coefficient
        P0_3Rm = -profileLoss_r*(P0_2Rm - P_2m)+P0_2Rm
        P_3m = P0_3Rm * hf.P_P0(gamma_t, Mw_3Rm)
        P0_3m = P_3m / hf.P_P0(gamma_t, Mc_3m)
        
        # Rotor solidity
        optimal_zweifel = 1
        fake_optimal_rotor_solidity = hf.sigXzweif(beta_2m, beta_3m) / optimal_zweifel     # "Optimal" solidity based on Zweifel
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
        num_stages_target = num_stages - 1 if num_stages != 1 else 1      # This will calculate a number for non-initial passes, but is meaningless unless it is the initial pass

        total_power_generated = sum([info.power for info in multistage_info])
        excess_power_margin = (total_power_generated - req_power_t)/req_power_t * 100

        if initial:
            r_mean_vec = [r_mean_i for _ in range(0, num_stages)]

        return REF_structs.Turbine_Pitchline_Results(multistage_velocity_triangles, multistage_info, r_mean_vec, total_power_generated, excess_power_margin, num_stages_target)