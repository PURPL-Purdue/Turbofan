from CoolProp.CoolProp import PropsSI
from CMYK.Object_Definitions.Base_Objects import Turbine
from Supplemental.Turbine import MAGENTA as mag
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

        rpm             = params.RPM        # RPM          TODO get rpm/ang_vel from 1d stress function for HPT

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
