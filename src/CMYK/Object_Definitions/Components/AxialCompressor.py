from CoolProp.CoolProp import PropsSI
from CMYK.Object_Definitions.Base_Objects import Compressor
import numpy as np
from CMYK.Run import helper_functions as hf

class AxialCompressor(Compressor):

    def __init__(self, name):
        super().__init__(name, 'FLOWPATH')

        # INLET AND EXIT FLOWS ================================
        self.FlowIn  = None
        self.FlowOut = None

        # INLET AND EXIT GEOMETRY INTERFACES ==================
        self.GeoIn  = None
        self.GeoOut = None

        # SHAFT CONNECTION ====================================
        self.Shaft = None

        # COMPONENT PARAMETERS ================================
        self.eta = None
        self.pr = None

        self.Wfactor = None
        self.Wstream = None

        # MAGENTA SIZING PARAMETERS
        self.gamma              = None
        self.Cp                 = None
        self.T0_1m              = None
        self.P0_1m              = None
        self.Pr_total           = None
        self.e_c                = None
        self.httrr              = None
        self.deHaller           = None
        self.min_Re             = None
        self.mu_kin             = None
        self.alpha_1m           = None
        self.Mz_1m              = None
        self.Mu_1t_max        = None
        self.m_dot              = None
        self.solidity_rotor     = None
        self.solidity_stator    = None

    def config(self) -> None:
        # CYAN Config ------------------
        cfg = self.cfg[self.name]
        super()._set_Wfactor()

        self.eta = cfg['eta']
        self.pr = cfg['pr_des']

        # MAGENTA Config ---------------
        self.e_c                = cfg['e_c']
        self.httrr              = cfg['httrr']
        self.deHaller           = cfg['deHaller']
        self.min_Re             = cfg['min_Re']
        self.alpha_1m           = np.radians(cfg['alpha_1m'])
        self.Mz_1m              = cfg['Mz_1m']
        self.Mu_1t_max          = cfg['Mu_1t_max']
        self.solidity_rotor     = cfg['solidity_R']
        self.solidity_stator    = cfg['solidity_S']

    #=====================================================
    #                   CMYK Methods
    ##=====================================================

    def CYAN(self):
        """Refer to CycleAnalysis.md for explanation of the math"""
        # PREPARING REQUIRED VALUES ---------------------
        h01 = self.FlowIn.h0
        P01 = self.FlowIn.P0
        s1 = self.FlowIn.s
        eta = self.eta
        pr = self.pr

        # P02 CALCULATION -------------------------------
        P02 = pr*P01

        # T02 CALCULATION -------------------------------
        P02s = P02
        s2s = s1
        h02s = PropsSI('HMASS', 'P', P02s, 'S', s2s, self.FlowIn.WF)
        h02 = (h02s-h01)/eta + h01
        T02 = PropsSI('T', 'P', P02, 'HMASS', h02, self.FlowIn.WF)

        # SET EXIT FLOW --------------------------------
        self.FlowOut.setFlow(
            T0=T02, P0=P02,
            Wfactor=self.Wfactor, Wstream=self.Wstream
        )

    def MAGENTA(self) -> None:
        gamma   = self.FlowIn.gamma0
        Cp      = self.FlowIn.Cp0
        T0_1m   = self.FlowIn.T0
        P0_1m   = self.FlowIn.P0
        m_dot   = self.FlowIn.W
        mu_kin = PropsSI('VISCOSITY', 'T', self.FlowIn.T0, 'P', self.FlowIn.P0, self.FlowIn.WF)

        Pr_total        = self.pr
        e_c             = self.e_c
        httrr           = self.httrr
        deHaller        = self.deHaller
        min_Re          = self.min_Re
        Mz_1m           = self.Mz_1m
        Mu_1t_max       = self.Mu_1t_max
        solidity_rotor  = self.solidity_rotor
        solidity_stator = self.solidity_stator
        alpha_1m        = np.radians(self.alpha_1m)

        # Compressor inlet conditions
        Mc_1m = Mz_1m / np.cos(alpha_1m)

        # Inlet Static Pressure and Temperature
        T_1m = T0_1m * hf.T_T0(gamma, Mc_1m)
        P_1m = P0_1m * hf.P_P0(gamma, Mc_1m)

        # Inlet flow characteristics
        R = (gamma - 1) * Cp / gamma                # TODO: CoolProp
        rho_1m = P_1m / (R * T_1m)                  # TODO: CoolProp
        a_1m = np.sqrt((gamma - 1) * Cp * T_1m)     # TODO: CoolProp
        z_1m = Mz_1m * a_1m
        C_1m = Mc_1m * a_1m

        # Initial inlet annulus geometry, assume constant spanwise distributions
        A_inlet = m_dot / rho_1m / z_1m
        r_tip_inlet = np.sqrt(A_inlet / (np.pi * (1 - httrr ** 2)))
        r_hub_inlet = r_tip_inlet * httrr

        # Compressor exit conditions
        # Tr_total = Pr_total ** ((gamma - 1) / (e_c * gamma))

        P0_exit_m = P0_1m * Pr_total  # at midspan
        T0_exit_m = self.FlowOut.T0   # at midspan
        Tr_total = T0_exit_m/T0_1m
        e_c = np.log(Pr_total)/np.log(Tr_total) * (gamma-1)/gamma

        alpha_exit_m = alpha_1m     # repeating stage design choice   | at midspan
        z_exit_m = z_1m             # design choice                   | at midspan
        C_exit_m = C_1m

        T_exit_m = T0_exit_m - C_exit_m ** 2 / (2 * Cp)             # | at midspan

        a_exit_m = np.sqrt((gamma - 1) * Cp * T_exit_m)          # TODO: CoolProp
        Mz_exit_m = z_exit_m / a_exit_m
        Mc_exit_m = Mz_exit_m / np.cos(alpha_exit_m)

        P_exit_m = P0_exit_m * hf.P_P0(gamma, Mc_exit_m)        # | at midspan
        rho_exit_m = P_exit_m / (R * T_exit_m)                  # TODO: CoolProp

        # Exit annulus geometry
        A_exit = m_dot / rho_exit_m / z_exit_m

        r_mean_1 = (r_tip_inlet + r_hub_inlet) / 2
        h = A_exit / (4 * np.pi * r_mean_1)

        r_hub_exit = r_mean_1 - h
        r_tip_exit = r_mean_1 + h

        error = 1
        first = True
        U_tip_inlet = Mu_1t_max * a_1m
        while error > 0.01:
            if not first:
                U_tip_inlet = U_tip_inlet - 0.5
            # ======== Pitchline calculations ========

            ang_vel = U_tip_inlet / r_tip_inlet
            rpm = ang_vel * 30 / np.pi

            # Station 1 stuff
            U_1m = U_tip_inlet * (r_mean_1 / r_tip_inlet)
            Ctheta_1m = z_1m * np.tan(alpha_1m)
            Wtheta_1m = U_1m - Ctheta_1m
            beta_1m = -np.atan(Wtheta_1m / z_1m)
            W_1m = z_1m / np.cos(beta_1m)
            Mw_1m = W_1m / a_1m

            # Station 2 stuff
            U_2m = U_1m  # Initial Approximation, true if we adjust both hub and shroud
            z_2m = z_1m  # Design choice

            W_2m = W_1m * deHaller  # De Haller
            beta_2m = np.acos(z_2m / W_2m)
            Wtheta_2m = z_2m * np.tan(beta_2m)
            Ctheta_2m = U_2m - Wtheta_2m

            C_2m = np.sqrt(z_2m ** 2 + Ctheta_2m ** 2)
            alpha_2m = np.atan(Ctheta_2m / z_2m)

            phi_2m = z_2m / U_2m
            psi_2m = 1 + phi_2m * (np.tan(-beta_2m) - np.tan(alpha_1m))

            T0_2m = T0_1m + U_1m * (Ctheta_2m - Ctheta_1m) / Cp
            T_2m = T0_2m - C_2m ** 2 / (2 * Cp)
            a_2 = np.sqrt((gamma - 1) * Cp * T_2m)

            Mc_2m = C_2m / a_2
            Mw_2m = W_2m / a_2
            Mz_2m = z_2m / a_2

            temp_rise_total = T0_exit_m - T0_1m
            temp_rise_per_stage = T0_2m - T0_1m
            num_stages_actual = temp_rise_total / temp_rise_per_stage

            if first:
                target = np.floor(num_stages_actual)
                first = False

            error = (num_stages_actual - target) / target
            print("tip_inlet: {:5.2f}     temp_rise: {:5.2f}     Ctheta_2m: {:5.2f}     Ctheta_1m: {:5.2f}     Ctheta 2-1: {:5.2f}     Wtheta_2m: {:5.2f}     Wtheta_1m: {:5.2f}".format(U_tip_inlet, temp_rise_per_stage, Ctheta_2m, Ctheta_1m, Ctheta_2m-Ctheta_1m, Wtheta_2m, Wtheta_1m))

        num_stages = int(np.round(num_stages_actual, 0))

        num_stations = num_stages * 2 + 1

        # Station 3 stuff
        C_3m = C_1m
        W_3m = W_1m
        U_3m = U_1m
        z_3m = z_1m
        Mc_3m = Mc_1m
        Mw_3m = Mw_1m
        Mz_3m = Mz_1m
        Ctheta_3m = Ctheta_1m
        Wtheta_3m = Wtheta_1m
        alpha_3m = alpha_1m
        beta_3m = beta_1m

        # Stage metrics
        degR_m = 1 - (Ctheta_1m + Ctheta_2m) / (2 * U_1m)
        D_mr = self.D_factor(W_1m, W_2m, Ctheta_1m, Ctheta_2m, solidity_rotor)
        D_ms = self.D_factor(C_2m, C_3m, Ctheta_2m, Ctheta_3m, solidity_stator)

        # RVT = REF_structs.FullVelTriInfo(
        #     C_1m, C_2m, C_3m,
        #     W_1m, W_2m, W_3m,
        #     U_1m, U_2m, U_3m,
        #     z_1m, z_2m, z_3m,
        #
        #     Mc_1m, Mc_2m, Mc_3m,
        #     Mw_1m, Mw_2m, Mw_3m,
        #     Mz_1m, Mz_2m, Mz_3m,
        #
        #     Ctheta_1m, Ctheta_2m, Ctheta_3m,
        #     Wtheta_1m, Wtheta_2m, Wtheta_3m,
        #
        #     alpha_1m, alpha_2m, alpha_3m,
        #     beta_1m, beta_2m, beta_3m,
        # )

        # StageInfo = {
        #     "degR_m": degR_m,
        #     "D_mr": D_mr,
        #     "D_ms": D_ms,
        #     "phi_2m": phi_2m,
        #     "psi_2m": psi_2m,
        # }

        # Per Stage State
        r_hub_vec = [1 for i in range(num_stages + 1)]
        r_tip_vec = [1 for i in range(num_stages + 1)]
        rho_m_vec = [1 for i in range(num_stages + 1)]
        T0_stages = [1 for i in range(num_stages + 1)]
        P0_stages = [1 for i in range(num_stages + 1)]
        Tr_stages = [1 for i in range(num_stages)]
        Pr_stages = [1 for i in range(num_stages)]

        T0_stages[0] = T0_1m
        P0_stages[0] = P0_1m

        r_hub_vec[0] = r_hub_inlet
        r_tip_vec[0] = r_tip_inlet

        T0_current = T0_1m
        for i in range(num_stages):
            T0_next = T0_current + temp_rise_per_stage
            Tr_stages[i] = T0_next / T0_current
            Pr_stages[i] = Tr_stages[i] ** (gamma * e_c / (gamma - 1))
            T0_stages[i + 1] = T0_next
            P0_stages[i + 1] = P0_stages[i] * Pr_stages[i]
            T0_current = T0_next

        # for i in range(num_stages + 1):
        #     r_hub_vec[i], r_tip_vec[i], rho_m_vec[i] = self.annulus_adjust(T0_stages[i], P0_stages[i],
        #                                                                                     R, gamma, m_dot, RVT.z_1m,
        #                                                                                     RVT.Mc_1m, r_mean_1)

        # Compressor Thermodynamics Total Metrics
        Pr_total_actual = np.prod(Pr_stages)
        Tr_total_actual = T0_stages[-1] / T0_stages[0]
        P0_rise_total = P0_stages[-1] - P0_stages[0]


        # AC_FF = HELP_Axial_Compressor.Compressor_Free_Vortex(RVT, r_hub_vec, r_tip_vec, ang_vel, degR_m, rho_m_vec, Cp,
        #                                                      R, T0_stages, m_dot, e_c, gamma)



    ##=====================================================
    #                   General Methods
    ##=====================================================
    def createCascades(self, sequence):
        """ USAGE NOTES:
        The "sequence" parameter defines a sequence of rotors and stators. The syntax of
        the sequence string must strictly adhere to the outlined convention with the letters
        'R' (for rotor) and 'S' (for stator) connected with an '>' as shown:
            R>S>R>S>R>S
        Inlet/exit guide vanes are treated as regular stators when setting up the cascade and
        should also be specified as an S:
            S>R>S>R>S
        """
        sequence = sequence.split('>')
        for row in sequence:
            if row == 'R':
                pass

    def 2D_geometry_MCA(self) -> None:
        pass
        """Mario and Josie, do your MCA code here"""

    @staticmethod
    def D_factor(W1, W2, Ctheta_1, Ctheta_2, sigma):
        # Diffusion factor, generally should be greater than 0.55 to prevent boundary layer separation
        D = 1 - W2 / W1 + abs(Ctheta_1 - Ctheta_2) / (2 * sigma * W1)
        return D

    @staticmethod
    def annulus_adjust(T0, P0, R, gamma, m_dot, z, Mc, r_mean):
        # Adjusts the annulus at a given station to meet mass flow rate
        T = T0 * hf.T_T0(gamma, Mc)  # | spanwise constant (design choice i think)
        P = P0 * hf.P_P0(gamma, Mc)  # | spanwise constant (design choice i think)
        rho_m = P / (R * T)

        A = m_dot / (rho_m * z)
        h = A / (4 * np.pi * r_mean)

        r_hub = r_mean - h
        r_tip = r_mean + h

        return [r_hub, r_tip, rho_m]

