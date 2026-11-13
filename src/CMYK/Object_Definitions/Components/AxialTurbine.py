from CoolProp.CoolProp import PropsSI
from Object_Definitions.Base_Objects import Turbine
from Object_Definitions.Supplemental.Turbine.MAGENTA import MAGENTA as mag
from Object_Definitions.Supplemental.Turbine.YELLOW import YELLOW as yel
from Object_Definitions.Base_Objects import BladeCoords
from Object_Definitions.Supplemental.Turbine.MAGENTA import Stress
import numpy as np

class AxialTurbine(Turbine):

    def __init__(self, name):
        """

        :param name: Either HPT or LPT
        """
        super().__init__(name, 'FLOWPATH')

        self.name = name
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
        self.N_Blades = 29
        self.operating_rpm = None
        self.num_stages = None

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
        self.N_Blades = int(cfg.get("N_Blades", self.N_Blades))
        self.initial_rpm = float(
            cfg.get("initial_rpm", 15000.0 if self.name == "HPT" else 8000.0)
        )
        self.r_mean_inlet = float(cfg.get("r_mean_inlet", 0.075))
        self.num_stages_target = cfg.get("num_stages_target")
        self.max_rpm_passes = int(cfg.get("max_rpm_passes", 100))
        self.max_power_passes = int(cfg.get("max_power_passes", 200))
        self.max_radius_passes = int(cfg.get("max_radius_passes", 200))
        self.rpm_derivative_lim = float(cfg.get("rpm_derivative_lim", 0.001))
        self.power_tolerance_pct = float(cfg.get("power_tolerance_pct", 2.0))
        self.damping_factor = float(cfg.get("damping_factor", 0.5))
        self.rpm_safety_factor = float(cfg.get("rpm_safety_factor", 0.85))
        self.degR_step = float(cfg.get("degR_step", 0.005))
        self.mean_radius_step = float(cfg.get("mean_radius_step", 0.01))

        self.rho_mat = float(cfg.get("rho_mat", 8190.0))
        self.yield_stress_mpa = float(cfg.get("yield_stress_mpa", 800.0))
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

        # exception handling before initialization
        if self.FlowIn is None or self.FlowOut is None:
            raise RuntimeError(f"{self.name}: flow interfaces are not connected")

        if self.GeoIn is None or self.GeoOut is None:
            raise RuntimeError(f"{self.name}: geometry interfaces are not connected")

        if self.Shaft is None:
            raise RuntimeError(f"{self.name}: shaft is not connected")
        # First stage stater is chosen by us based on previus stuff
        # Max rpm will be based on first stage, where it is the hottest
        gamma   = self.FlowIn.gamma0
        Cp      = self.FlowIn.Cp0
        R       = self.FlowIn.R
        T0_in   = self.FlowIn.T0        # HPT inlet total temperature, K
        P0_in   = self.FlowIn.P0        # HPT inlet total pressure,    Pa
        m_dot   = self.FlowIn.W         # Turbine total mass flow, kg/s, air plus fuel

        self.Wfactor = self.FlowIn.Wfactor

        req_power = self.Shaft.required_power
        if req_power is None or req_power <= 0:
            raise RuntimeError(
                f"{self.name}: shaft required_power must be positive and an integer"
            )

        if hasattr(self.GeoIn, "alpha_out"):
            alpha_in = self.GeoIn.alpha_out
            r_mean_inlet = self.GeoIn.r_mean_out
        else:
            alpha_in = self.alpha_1m
            r_mean_inlet = self.r_mean_inlet

        # First stage design decisions
        alpha_1m        = self.alpha_1m
        alpha_2m        = self.alpha_2m
        Mc_2m           = self.Mc_2m                      # Slightly supersonic stator nozzle exit
        Mw_3Rm          = self.Mw_3Rm                     # TODO find justification for this

        # Multistage design decisions
        Mc_2m_default   = self.Mc_2m_default              # Just barely not choking the flow at stator nozzle exit
        Mw_3Rm_default  = self.Mw_3Rm_default             # TODO find justification for this


        # ================= VARIABLES FOR ITERATION =================
        # max_passes = 100
        # rpm_derivative_lim = 0.001  # 0.1% relative convergence tolerance
        # damping_factor = 0.5
        # rpm_safety_factor = 0.85  # Operating RPM = 85% of max structural RPM
        # # ======== Stress variables ========
        # r_mean_inlet = 0.075  # HPT inlet mean radius, m
        # rho_mat = 8190.0  # Inconel density, kg/m^3
        # yield_stress_mpa = 800.0  # Inconel yield stress, MPa

        # -----------------------------------------------------
        #  PART 1:
        # -----------------------------------------------------
        # rpm_HPT = 15000  # Initial RPM for HPT
        # implement
        for i in range(self.max_rpm_passes):
            # These variables need to be reinitialized between every pass TODO: Figure out if degreeR_m needs to changed after the initial pass
            ang_vel = self.initial_rpm * 2 * np.pi / 60 # Angular velocity, rad/s
            degR_m = self.degR_m
            r_mean_inlet = self.r_mean_inlet
            r_inc_factor = 0

            if self.name.upper() == "HPT" or (self.name.upper() == "LPT" and self.num_stages_target is None):
                percent_error = 5
                while percent_error > 2 or percent_error < 0:
                    pitchline_res  = mag.pitchline_staging(
                        False,  # initial
                        Mc_2m,
                        Mw_3Rm,
                        Mc_2m_default,
                        Mw_3Rm_default,
                        alpha_in,
                        alpha_2m,
                        T0_in,
                        P0_in,
                        r_mean_inlet,
                        ang_vel,
                        gamma,
                        R,
                        Cp,
                        m_dot,
                        degR_m,
                        req_power,
                        r_inc_factor=0.0,
                        num_stages_target=1
                    )
                    total_power = pitchline_res .total_power_generated
                    percent_error = (total_power - req_power) / req_power * 100
                    if percent_error < 0:
                        degR_m += 0.005
                    else:
                        degR_m -= 0.005
            elif self.name.upper() == "LPT" and self.num_stages_target is not None:
                while total_power < req_power:
                    pitchline_res = mag.pitchline_staging(
                        False,  # initial
                        Mc_2m,
                        Mw_3Rm,
                        Mc_2m_default,
                        Mw_3Rm_default,
                        alpha_1m,
                        alpha_2m,
                        T0_in,
                        P0_in,
                        r_mean_inlet,
                        ang_vel,
                        gamma,
                        R,
                        Cp,
                        m_dot,
                        degR_m,
                        req_power,
                        r_inc_factor=r_inc_factor,
                        num_stages_target=self.num_stages_target
                    )
                    total_power = pitchline_res.total_power_generated
                    r_mean_curr += 0.01
                    r_inc_factor += 0.01
            else:
                raise ValueError("Assign correct name to Turbine object ('HPT' or 'LPT') and initialize num_stages_target")

            vt = pitchline_res.multistage_velocity_triangles[0]
            info = pitchline_res.multistage_info[0]
            r_hub, r_tip, _ = mag.annulus_adjust(
                info.T0_3m, info.P0_3m, R, gamma,
                m_dot, vt.z_3m, vt.Mc_3m, r_mean_inlet
            )
            blade_length = r_tip - r_hub

            # ======== Stress calculation ========
            rpm_HPT_new = self.rpm_safety_factor * Stress.get_max_rpm_light(self.rho_mat, self.yield_stress_mpa,
                                                                            r_mean_inlet, blade_length)

            rpm_derivative = abs(rpm_HPT_new - rpm_HPT) / rpm_HPT

            if rpm_derivative < self.rpm_safety_factor:
                print(f"HPT Converged at {rpm_HPT:.1f} RPM (1 stage)")
                break

            rpm_HPT = (1.0 - self.damping_factor) * rpm_HPT + self.damping_factor * rpm_HPT


        # -----------------------------------------------------
        #  PART 3:
        # -----------------------------------------------------
        vt_last = self.pitchline_res.multistage_velocity_triangles[-1]
        info_last = self.pitchline_res.multistage_info[-1]
        r_mean_last = self.pitchline_res.r_mean_vec[-1]

        self.FlowOut.setFlow(
            T0=info_last.T0_3m,
            P0=info_last.P0_3m,
            FAR=self.FlowIn.FAR,
            Wfactor=self.Wfactor,
            Wstream=self.Wstream
        )
        self.GeoOut.alpha_out = vt_last.alpha_3m
        self.GeoOut.r_mean_out = r_mean_last

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

        def rad_eq(theta, r_tip, r_hub, r_mega_tip, r_mega_hub, type, inorout):
            theta = np.deg2rad(theta)

            if type == "stator" or (type == "rotor" and inorout == "in"):
                V_mag = 525
                V_theta_M = V_mag * np.sin(theta)
                r_mid = (r_hub + r_tip) / 2

                K = V_theta_M * r_mid

                V_theta_H = K / r_hub
                V_theta_T = K / r_tip
                V_theta_mH = K / r_mega_hub
                V_theta_mT = K / r_mega_tip

                beta_H = np.rad2deg(np.arctan(V_theta_H / (V_mag * np.cos(theta))))
                beta_T = np.rad2deg(np.arctan(V_theta_T / (V_mag * np.cos(theta))))
                beta_mH = np.rad2deg(np.arctan(V_theta_mH / (V_mag * np.cos(theta))))
                beta_mT = np.rad2deg(np.arctan(V_theta_mT / (V_mag * np.cos(theta))))
            elif (type == "rotor" and inorout == "out"):
                V_mag = 277
                V_theta_M = V_mag * np.sin(theta)
                r_mid = (r_hub + r_tip) / 2

                K = V_theta_M * r_mid

                V_theta_H = K / r_hub
                V_theta_T = K / r_tip
                V_theta_mH = K / r_mega_hub
                V_theta_mT = K / r_mega_tip

                beta_H = np.rad2deg(np.arctan(V_theta_H / (V_mag * np.cos(theta))))
                beta_T = np.rad2deg(np.arctan(V_theta_T / (V_mag * np.cos(theta))))
                beta_mH = np.rad2deg(np.arctan(V_theta_mH / (V_mag * np.cos(theta))))
                beta_mT = np.rad2deg(np.arctan(V_theta_mT / (V_mag * np.cos(theta))))

            return beta_H, beta_T, beta_mH, beta_mT

        vel_triangles = self.pitchline_res.multistage_velocity_triangles
        stage_info = self.pitchline_res.multistage_info
        r_mean_vec = self.pitchline_res.r_mean_vec

        num_stages = self.pitchline_res.num_stages_target

        self.blade_profiles = []

        for i in range(num_stages):
            vt = vel_triangles[i]
            info = stage_info[i]

            R_stator = R_rotor = r_mean_vec[i]

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