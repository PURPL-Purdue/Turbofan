from CoolProp.CoolProp import PropsSI
from CMYK.Object_Definitions.Base_Objects import ComponentBase

class Inlet(ComponentBase):

    def __init__(self, name):
        super().__init__(name, 'FLOWPATH')

        # INLET AND EXIT FLOWS --------------------------------
        self.FlowIn  = None
        self.FlowOut = None

        # INLET AND EXIT GEOMETRY INTERFACES ------------------
        self.GeoIn  = None
        self.GeoOut = None

        # COMPONENT PROPERTIES --------------------------------
        self.eta = None

        self.Wfactor = None
        self.Wstream = None

    def config(self) -> None:
        cfg = self.cfg[self.name]
        super()._set_Wfactor()

        self.eta = cfg['eta']



    #-----------------------------------------------------
    #                   CMYK Methods
    #-----------------------------------------------------

    def CYAN(self):
        """Refer to CycleAnalysis.md for explanation of the math"""
        # PREPARING REQUIRED VALUES ---------------------
        h1 = self.FlowIn.h
        h01 = self.FlowIn.h0
        T01 = self.FlowIn.T0
        s1 = self.FlowIn.s
        eta = self.eta

        # T02 CALCULATION -------------------------------
        T02 = T01

        # P02 CALCULATION -------------------------------
        h02 = h01
        h02s = eta*(h02-h1) + h1
        s2s = s1
        P02s = PropsSI('P', 'HMASS', h02s, 'S', s2s, self.FlowIn.WF)
        P02 = P02s

        # SET EXIT FLOW ---------------------------------
        self.FlowOut.setFlow(
            T0=T02, P0=P02,
            Wfactor=self.Wfactor, Wstream=self.Wstream
        )