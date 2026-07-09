from CoolProp.CoolProp import PropsSI
from CMYK.Object_Definitions.Base_Objects import ComponentBase
import CMYK.Run.helper_functions as hf
import numpy as np

class Nozzle(ComponentBase):

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

        # COMPONENT PROPERTIES -------------------------------
        self.eta = None

        self.P_amb = None
        self.design_mode = None

        self.Wfactor = None
        self.Wstream = None

        self.u_exit = None
    
    def config(self) -> None:
        """See CycleAnalysis.md for self.design_mode usage"""
        cfg = self.cfg[self.name]
        self.Wstream = cfg['Wstream']

        self.eta = cfg['eta']
        self.P_amb = self.cfg['AMB_FS']['P_0']

        self.design_mode = cfg['design_mode']


    def calcExitVelocity(self) -> None:
        self.u_exit = np.sqrt(2*self.eta *(self.FlowIn.gamma /(self.FlowIn.gamma -1))*self.FlowIn.R*self.FlowIn.T0*(1 - (self.FlowOut.P/self.FlowIn.P0)**((self.FlowIn.gamma-1)/self.FlowIn.gamma)))


    def sizing(self) -> None:
        P2 = self.P_amb
        P01 = self.FlowIn.P0

        NPR = P01 / P2
        NPR_crit = 1 / hf.P_P0(self.FlowIn.gamma0,1)  # # TODO: KNOWN INACCURACY: When using isentropic relations, static gamma should be used.
        choked = False
        if NPR < 1:
            raise RuntimeError("Nozzle CYAN(): Nozzle inlet total pressure less than ambient static pressure.")
        elif NPR > NPR_crit:
            choked = True
    #-----------------------------------------------------
    #                   CMYK Methods
    #-----------------------------------------------------

    def CYAN(self):
        # PREPARING REQUIRED VALUES ---------------------
        self.Wfactor = self.FlowIn.Wfactor
        P2 = self.P_amb
        s2s = self.FlowIn.s
        h01 = self.FlowIn.h0
        P01 = self.FlowIn.P0
        T02 = self.FlowIn.T0
        eta = self.eta

        # CHECK FOR INVALID NOZZLE PRESSURE RATIO
        if P01 / P2 < 1:
            raise RuntimeError("Nozzle CYAN(): Nozzle inlet total pressure less than ambient static pressure.")
        # T2 CALCULATION ----------------------------------
        P2s = P2
        h2s = PropsSI('HMASS', 'P', P2s, 'S', s2s, self.FlowIn.WF)
        h2 = eta*(h2s-h01) + h01
        T2 = PropsSI('T', 'HMASS', h2, 'P', P2, self.FlowIn.WF)

        # M2 CALCULATION --------------------------------
        M2 = hf.M_fromTT0(self.FlowIn.gamma0, float(T2), T02) # TODO: KNOWN INACCURACY: When using isentropic relations, static gamma should be used.

        # SET EXIT FLOW ---------------------------------
        self.FlowOut.setFlow(
            T=T2, P=P2, FAR=self.FlowIn.FAR, M=M2,
            Wfactor=self.Wfactor, Wstream=self.Wstream
        )

