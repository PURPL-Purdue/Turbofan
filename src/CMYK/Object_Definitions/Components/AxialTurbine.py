from CoolProp.CoolProp import PropsSI
from CMYK.Object_Definitions.Base_Objects import Turbine

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