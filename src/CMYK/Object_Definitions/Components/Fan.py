from CoolProp.CoolProp import PropsSI
from CMYK.Object_Definitions.Base_Objects import Compressor

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

        self.Wfactor = None
        self.Wstream = None

    def config(self) -> None:
        cfg = self.cfg[self.name]
        super()._set_Wfactor()

        self.eta = cfg['eta']
        self.pr  = cfg['pr_des']
        self.bypass = cfg['bypass']


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
        pass
