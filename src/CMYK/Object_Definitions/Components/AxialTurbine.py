from CoolProp.CoolProp import PropsSI
from Object_Definitions.Base_Objects import Turbine
from Object_Definitions.Supplemental.Turbine.MAGENTA import MAGENTA as mag
from Object_Definitions.Supplemental.Turbine.YELLOW import YELLOW as yel
from Object_Definitions.Base_Objects import BladeCoords
from Object_Definitions.Supplemental.Turbine.MAGENTA import Stress
import numpy as np

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

        # -----------------------------------------------------
        #          Used in YELLOW
        # -----------------------------------------------------
        self.pitchline_res = None
        self.blade_profiles = None
        self.N_Blades = 29 # Don't know if number of blades should be hardcoded or not

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


        # TODO Finish finding values for old variables or delete unused ones
        # ================= OLD CODE VARIABLE INPUTS =================
        # TODO: Verify if m_dot_cool, T0_cool, P0_cool, and ep are actually not needed
        # m_dot_cool      = params.m_dot_cool # Cooling air bleedoff mass flow, kg/s
        # T0_cool         = params.T0_cool    # Cooling air temperature, kelvin
        # P0_cool         = params.P0_cool    # Cooling air pressure, Pa
        #
        # ep              = params.ep

        # ================= END OLD CODE VARIABLE INPUTS =================

        # ================= VARIABLES FOR ITERATION =================
        rpm_i = 15000  # initial RPM
        max_passes = 10000 # arbitrary number for now TODO: Measure runtime of a single loop pass and update max_passes
        rpm_derivative_lim = 0.001 # sets the secondary condition for when the loop iteration will stop
        damping_factor = 0.5 # damping factor to prevent oscillation between small and large RPMs by the solver

        # ======== Stress variables ========
        # TODO: Verify which variables come from where
        density = 8190  # inconel, kg/m^3
        yield_stress = 800  # inconel, MPa
        radius_hub = 0.05  # hub radius, m
        mfr = 100  # mass flow rate, kg/s
        v_in = 100  # velo air in, m/s
        v_out = 500  # velo air out, m/s
        n_b = self.N_Blades  # number of blades
        start = 0.005  # start blade length, m
        end = 0.05  # end blade length, m
        num = 50  # num of test points
        blade_length = # m

        for i in range(max_passes):
            # These variables need to be reinitialized between every pass TODO: Figure out if degreeR_m needs to changed after the initial pass
            r_mean_i = 0.075 # Inlet pitchline radius, meters    TODO get new formulation for r_mean_i (originally comes from LPC)
            ang_vel = rpm * 2 * np.pi / 60 # Angular velocity, rad/s
            total_power_generated = 0
            r_inc_factor = 0
            degR_m = self.degR_m

            # Old code power calculations :
            # removed since power is now calculated by shaft
            #
            # ======== Whole Turbine Calcs (absolute station numbers) ========
            #power_c = m_dot_c * Cp_c * (T0_3-T0_2)          # Power required by compressor
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

            # ======== Preliminary mean line blade coord generation========
            meanline_slice = YELLOW

            # ======== Stress calculation ========

            rpm_safety_factor = 0.85 # this is just a guess, change as needed
            rpm = rpm_safety_factor * Stress.get_max_rpm(meanline_slice, density, yield_stress, radius_hub, mfr, v_in, v_out, n_b, blade_length)
            rpm_derivative = abs(rpm - rpm_i) / rpm_i
            if rpm_derivative > rpm_safety_factor < rpm_derivative_lim:
                print(f"Converged at {float(rpm):.1f} RPM!")
                break

            rpm_i = (1.0 - damping_factor) * rpm_i + damping_factor * rpm

        self.pitchline_res = pitchline_res
        mag.Turbine_Annulus_Sizing(
            pitchline_res.multistage_velocity_triangles,
            pitchline_res.multistage_info,
            m_dot,
            gamma,
            R,
            pitchline_res.r_mean_vec
        )

        return

    # TODO: Add comments and improve on OOP practices
    def YELLOW(self) -> None:
        """
        After getting the final mean line velocity triangles from MAGENTA, use radial equilibrium function to get spanwise velocity triangles
        :return: does note explicitly return anything but makes the whole 3D blade profile
        """

        vel_triangles = self.pitchline_res.multistage_velocity_triangles
        stage_info = self.pitchline_res.multistage_info
        r_mean_vec = self.pitchline_res.r_mean_vec

        num_stages = self.pitchline_res.num_stages_target

        self.blade_profiles = []

        for i in range(num_stages):
            vt = vel_triangles[i]
            info = stage_info[i]

            R_stator = r_mean_vec[i]
            R_rotor = r_mean_vec[i]

            stator_params = list([
                R_stator,
                vt.alpha_1m,  # Stator inlet angle
                vt.alpha_2m,  # Stator exit angle
                self.N_Blades,
                info.Mc_2m  # Stator absolute exit Mach
            ])

            rotor_params = list([
                R_rotor,
                vt.beta_2m,  # Rotor relative inlet angle
                vt.beta_3m,  # Rotor relative exit angle
                self.N_Blades,
                info.Mw_3Rm  # Rotor relative exit Mach
            ])

            stator_geom = yel.YELLOW(*stator_params)
            rotor_geom = yel.YELLOW(*rotor_params)

            self.blade_profiles.append({
                'stage': i + 1,
                'stator': stator_geom,
                'rotor': rotor_geom
            })

        return