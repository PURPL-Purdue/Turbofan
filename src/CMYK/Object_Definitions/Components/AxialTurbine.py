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
        #            Flow Inlets and Exits
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
        self.annulus_res = None

        # -----------------------------------------------------
        #          USED IN YELLOW
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
        """
        Size the axial turbine using pitchline staging, power matching,
        and structural RPM constraints.

        Supports both single-stage and multistage turbines.

        Stage selection:
            - If num_stages_target is specified, use that stage count.
            - If num_stages_target is None, estimate the required stage count.

        Power matching:
            - Single stage: adjust degree of reaction.
            - Multiple stages: adjust mean radius and radial increment.

        The method only operates on this turbine instance. Upstream and
        downstream components communicate through Flow and GeometryInterface.
        """

        # -----------------------------------------------------
        #                  INPUT DATA VALIDATION
        # -----------------------------------------------------

        if self.FlowIn is None or self.FlowOut is None:
            raise RuntimeError(f"{self.name}: flow interfaces are not connected")

        if self.GeoIn is None or self.GeoOut is None:
            raise RuntimeError(f"{self.name}: geometry interfaces are not connected")

        if self.Shaft is None:
            raise RuntimeError(f"{self.name}: shaft is not connected")

        # -----------------------------------------------------
        #                  INLET CONDITIONS
        # -----------------------------------------------------

        gamma = self.FlowIn.gamma0
        Cp = self.FlowIn.Cp0
        R = self.FlowIn.R

        T0_in = self.FlowIn.T0
        P0_in = self.FlowIn.P0

        m_dot = self.FlowIn.W

        self.Wfactor = self.FlowIn.Wfactor

        # Required power is either determined by HPC or LPC through Shaft
        req_power = self.Shaft.required_power

        if req_power is None or req_power <= 0:
            raise RuntimeError(f"{self.name}: shaft required_power must be positive")

        # Use upstream geometry when available.
        # Otherwise, use the configured initial design conditions.

        alpha_in = getattr(self.GeoIn, "alpha_out", None)
        r_mean_inlet = getattr(self.GeoIn, "r_mean_out", None)

        if alpha_in is None:
            alpha_in = self.alpha_1m

        if r_mean_inlet is None:
            r_mean_inlet = self.r_mean_inlet

        # -----------------------------------------------------
        #                  DESIGN PARAMETERS
        # -----------------------------------------------------

        alpha_2m = self.alpha_2m

        Mc_2m = self.Mc_2m
        Mw_3Rm = self.Mw_3Rm

        Mc_2m_default = self.Mc_2m_default
        Mw_3Rm_default = self.Mw_3Rm_default

        rpm = self.initial_rpm

        # -----------------------------------------------------
        #                 MAIN RPM ITERATION
        # -----------------------------------------------------
        # note that for ... else loop runs the else if the loop finishes without hitting break
        for rpm_pass in range(self.max_rpm_passes):
            # Reset sizing variables for this RPM iteration.
            ang_vel = rpm * 2.0 * np.pi / 60.0
            degR_m = self.degR_m
            r_mean_i = r_mean_inlet
            r_inc_factor = 0.0

            # determine number of stages
            if self.num_stages_target is None:
                initial_pitchline_res = mag.pitchline_staging(
                    True,  # Initial
                    Mc_2m,
                    Mw_3Rm,
                    Mc_2m_default,
                    Mw_3Rm_default,
                    alpha_in,
                    alpha_2m,
                    T0_in,
                    P0_in,
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
            else:
                # Use the stage count specified in the configuration
                num_stages_target = self.num_stages_target

            if num_stages_target is None or num_stages_target < 1:
                raise RuntimeError(f"{self.name}: invalid number of stages: {num_stages_target}")

            # -------------------------------------------------
            #                  POWER MATCHING
            # -------------------------------------------------
            if num_stages_target == 1:
                # =============================================
                #              SINGLE-STAGE TURBINE
                # =============================================
                # Match generated power by adjusting degree of reaction.
                for power_pass in range(self.max_power_passes):
                    pitchline_res = mag.pitchline_staging(
                        False,
                        Mc_2m,
                        Mw_3Rm,
                        Mc_2m_default,
                        Mw_3Rm_default,
                        alpha_in,
                        alpha_2m,
                        T0_in,
                        P0_in,
                        r_mean_i,
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
                    total_power_generated = pitchline_res.total_power_generated
                    percent_error = ((total_power_generated - req_power) / req_power * 100.0)

                    # Accept a solution with the required power and an oversizing error within tolerance
                    if 0.0 <= percent_error <= self.power_tolerance_pct:
                        break

                    # Adjust reaction according to power error
                    if percent_error < 0.0:
                        degR_m += self.degR_step
                    else:
                        degR_m -= self.degR_step
                else:
                    raise RuntimeError(
                        f"{self.name}: single-stage power matching "
                        f"did not converge. Final error: {percent_error:.2f}%"
                    )
            else:

                # =============================================
                #             MULTISTAGE TURBINE
                # =============================================
                # Match generated power by adjusting the mean radius and radial increment
                for radius_pass in range(self.max_radius_passes):
                    pitchline_res = mag.pitchline_staging(
                        False,
                        Mc_2m,
                        Mw_3Rm,
                        Mc_2m_default,
                        Mw_3Rm_default,
                        alpha_in,
                        alpha_2m,
                        T0_in,
                        P0_in,
                        r_mean_i,
                        ang_vel,
                        gamma,
                        R,
                        Cp,
                        m_dot,
                        degR_m,
                        req_power,
                        r_inc_factor=r_inc_factor,
                        num_stages_target=num_stages_target
                    )

                    total_power_generated = pitchline_res.total_power_generated
                    # The original multistage approach increases the radius until sufficient power is generated.
                    if total_power_generated >= req_power:
                        break

                    r_mean_i += self.mean_radius_step
                    r_inc_factor += self.mean_radius_step
                else:
                    raise RuntimeError(f"{self.name}: multistage power matching did not converge within {self.max_radius_passes} iterations")

            # -------------------------------------------------
            #              STRUCTURAL RPM CALCULATION
            # -------------------------------------------------
            # use first stage for HPT and last stage for LPT stress calculations
            if self.name.upper() == "LPT":
                vt = pitchline_res.multistage_velocity_triangles[-1]
                info = pitchline_res.multistage_info[-1]
                r_mean_stage = pitchline_res.r_mean_vec[-1]
            else:
                vt = pitchline_res.multistage_velocity_triangles[0]
                info = pitchline_res.multistage_info[0]
                r_mean_stage = pitchline_res.r_mean_vec[0]

            r_hub, r_tip, _ = mag.annulus_adjust(
                info.T0_3m,
                info.P0_3m,
                R,
                gamma,
                m_dot,
                vt.z_3m,
                vt.Mc_3m,
                r_mean_stage
            )

            blade_length = r_tip - r_hub
            rpm_max = self.rpm_safety_factor * Stress.get_max_rpm_light(self.rho_mat, self.yield_stress_mpa, r_mean_stage, blade_length)
            rpm_derivative = abs(rpm_max - rpm) / rpm

            if rpm_derivative < self.rpm_derivative_lim:
                self.operating_rpm = rpm
                print(f"{self.name} converged at {rpm:.1f} RPM ({num_stages_target} stages)")
                break
            # damped update to prevent RPM oscillation
            rpm = ((1.0 - self.damping_factor) * rpm + self.damping_factor * rpm_max)
        else:
            raise RuntimeError(f"{self.name}: RPM iteration did not converge within {self.max_rpm_passes} passes")

        # -----------------------------------------------------
        #                  STORE FINAL RESULTS
        # -----------------------------------------------------
        self.num_stages = num_stages_target

        vt_last = pitchline_res.multistage_velocity_triangles[-1]
        info_last = pitchline_res.multistage_info[-1]
        r_mean_last = pitchline_res.r_mean_vec[-1]

        # update exit parameters
        self.FlowOut.setFlow(
            T0=info_last.T0_3m,
            P0=info_last.P0_3m,
            FAR=self.FlowIn.FAR,
            Wfactor=self.Wfactor,
            Wstream=self.Wstream
        )
        self.GeoOut.alpha_out = vt_last.alpha_3m
        self.GeoOut.r_mean_out = r_mean_last

        # output values for annulus sizing
        self.pitchline_res = pitchline_res
        self.operating_rpm = rpm
        self.annulus_res = mag.Turbine_Annulus_Sizing(
            pitchline_res.multistage_velocity_triangles,
            pitchline_res.multistage_info,
            m_dot,
            gamma,
            R,
            pitchline_res.r_mean_vec
        )


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