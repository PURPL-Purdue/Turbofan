from CoolProp.CoolProp import PropsSI
from CMYK.Object_Definitions.Base_Objects import Compressor
import numpy as np

class Fan(Compressor):

    def __init__(self, name):
        super().__init__(name, 'FLOWPATH')

        # INLET AND EXIT FLOWS --------------------------------
        self.FlowIn      = None
        self.FlowOut_COR = None
        self.FlowOut_BYP = None

        # INLET AND EXIT GEOMETRY INTERFACES ------------------
        self.GeoIn      = None
        self.GeoOut_COR = None
        self.GeoOut_BYP = None

        # SHAFT CONNECTION ------------------------------------
        self.Shaft = None

        # COMPONENT PROPERTIES --------------------------------
        self.eta = None
        self.pr = None
        self.bypass = None
        self.Mu_1t_max = None

        self.constantRad = None

        self.Wfactor = None
        self.Wstream = None

    def config(self) -> None:
        cfg = self.cfg[self.name]
        super()._set_Wfactor()

        self.eta = cfg['eta']
        self.pr  = cfg['pr_des']
        self.bypass = cfg['bypass']
        self.Mu_1t_max = cfg['Mu_1t_max']
        self.constantRad = cfg['constantRad']

    #-----------------------------------------------------
    #                   CMYK Methods
    #-----------------------------------------------------

    def CYAN(self):
        """Refer to CycleAnalysis.md for explanation of the math"""
        # PREPARING REQUIRED VALUES ---------------------
        h01 = self.FlowIn.h0
        P01 = self.FlowIn.P0
        s1 = self.FlowIn.s
        eta = self.eta
        pr = self.pr

        # P02 CALCULATION -------------------------------
        P02 = pr * P01

        # T02 CALCULATION -------------------------------
        P02s = P02
        s2s = s1
        h02s = PropsSI('HMASS', 'P', P02s, 'S', s2s, self.FlowIn.WF)
        h02 = (h02s - h01) / eta + h01
        T02 = PropsSI('T', 'P', P02, 'HMASS', h02, self.FlowIn.WF)

        # SET EXIT FLOWS --------------------------------
        self.FlowOut_COR.setFlow(
            T0=T02, P0=P02,
            Wfactor=1, Wstream='CORE'
        )
        self.FlowOut_BYP.setFlow(
            T0=T02, P0=P02,
            Wfactor=self.bypass, Wstream='BYPASS'
        )

    def MAGENTA(self):
        # Unpacking FlowIn values
        gamma = self.FlowIn.gamma
        Cp = self.FlowIn.Cp

        bypassRatio = params.bypass

        M_tip_inlet_max = self.Mu_1t_max
        C_1 = self.FlowIn.VT.C
        R = self.FlowIn.R
        M_1 = self.FlowIn.VT.Mc_1  # inlet mach number
        T01 = self.FlowIn.T0
        P01 = self.FlowIn.P0
        mdot_1 = self.FlowIn.W
        np = self.eta  # polytropic efficiency (decimal)
        Pr = self.pr  # input pressure ratio
        Tr = np.pow(Pr, (gamma - 1) / gamma * np)
        constantRad = self.constantRad # ("hub", "tip", or "mean"); determines what characteristic remains constant for inlet annulus calculation

        # CALCULATIONS ------------------------
        # check muhehehe
        T1 = T01 * REF_AEQ.T_T0(gamma, M_1)  # static temp
        a1 = REF_AEQ.a(gamma, R, T1)  # speed of sound

        # ======== Inlet Annulus ========
        rho01 = P01 / (R * T01)
        A_1 = mdot_1 / (rho01 * C_1)

        if constantRad == "hub":

            r_hub_1 = params.r_hub_1
            r_tip_1 = m.sqrt((A_1 / m.pi) + r_hub_1 ** 2)
            htftrr = r_hub_1 / r_tip_1

        elif constantRad == "tip":

            r_tip_1 = params.r_tip_1
            r_hub_1 = m.sqrt(r_tip_1 ** 2 - (A_1 / m.pi))
            htftrr = r_hub_1 / r_tip_1

        elif constantRad == "mean":

            htftrr = params.htftrr
            r_hub_1 = m.sqrt((A_1 * htftrr ** 2) / (m.pi * (1 - htftrr ** 2)))
            r_tip_1 = r_hub_1 / htftrr

        else:
            print("Check for typos goober")

        # local station 1 velocity triangle calculations :thumbsup:
        U_tip_inlet = M_tip_inlet_max * a1  # tangential velocity of fan tip based on max mach number we want
        omega = U_tip_inlet / r_tip_1  # angular velocity
        r_mean = (r_hub_1 + r_tip_1) / 2  # constant
        # ========================================================================================

        # fix code attempt!!! (numerical integration or something)
        # ======== Mass Flow Along Blade Span ========
        num_increments = 100  # input desired number of dividends along blade span (higher num = higher accuracy)
        T02 = Tr * T01
        P02 = Pr * P01
        rho02 = P02 / (R * T02)
        z_2m = C_1

        r_hub_2 = r_hub_1  # temporary initial values
        r_tip_2 = r_tip_1  # temporary initial values
        mdot_2 = 0  # temporary initial values
        rho_2_vec = np.zeros((1, num_increments + 1))
        C_2_vec = np.zeros((1, num_increments + 1))
        r_2_vec = np.zeros((1, num_increments + 1))
        massflowConditionMet = False

        while not massflowConditionMet:

            dr = (r_tip_2 - r_hub_2) / num_increments
            r_i = r_hub_2
            for i in range(num_increments + 1):
                # C along span
                U_i = omega * r_i
                Ctheta_2i = Cp * (T02 - T01) / U_i
                C_i = m.sqrt(Ctheta_2i ** 2 + z_2m ** 2)
                C_2_vec[i] = C_i

                # rho along span
                T2_i = T02 - (C_i ** 2 / (2 * Cp))
                rho_2i = rho02 * m.pow((T2_i / T02), (1 / (gamma - 1)))
                rho_2_vec[i] = rho_2i

                # annulus radii along span
                r_i += dr
                r_2_vec[i] = r_i

            # total station 2 mass flow
            mdot_2 = mass_flow(rho_2_vec, C_2_vec, r_2_vec)

            if abs(mdot_2 - mdot_1) <= 0.001:
                massflowConditionMet = True

            else:

                # iterate r_hub and r_tip based on constant r_mean
                A_2_current = m.pi * (r_tip_2 ** 2 - r_hub_2 ** 2)
                A_2_actual = A_2_current * mdot_1 / mdot_2
                h = A_2_actual / (4 * m.pi * r_mean)
                r_hub_2 = r_mean - h
                r_tip_2 = r_mean + h

        j = 0
        coreFlow = 0
        bypassConditionMet = False
        while not bypassConditionMet:
            rho_avg = (rho_2_vec[j] + rho_2_vec[j + 1]) / 2
            V_avg = (C_2_vec[j] + C_2_vec[j + 1]) / 2
            area = m.pi * ((r_2_vec[j] + r_2_vec[j + 1]) ** 2 - (r_2_vec[j]) ** 2)
            coreFlow += rho_avg * V_avg * area

            if (((mdot_2 - coreFlow) / coreFlow) >= bypassRatio):
                bypassConditionMet = True

            else:
                j += 1

        r_LPC_tip = r_2_vec[j]
        # ========================================================================================

        # TODO: confirm whether these calculations are for fan outlet or compressor inlet (r_mean may differ?)
        r_mean = (r_LPC_tip + r_hub_2) / 2
        U_m = r_mean * omega  # **
        alpha_1 = m.atan(U_m / C_1)  # **
        w_magnitude = C_1 / m.sin(alpha_1)  # **

        # local station 3 velocity triangle calculations
        # Cp = gamma / (gamma - 1) * R
        C_theta2 = Cp * (T02 - T01) / U_m
        alpha_2 = m.atan((U_m - C_theta2) / C_1)  # **
        w_magnitude_2 = C_1 / m.sin(alpha_2)  # **

        pass