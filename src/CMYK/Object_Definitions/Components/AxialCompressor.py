from CoolProp.CoolProp import PropsSI
from CMYK.Object_Definitions.Base_Objects import Compressor

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

    def config(self) -> None:
        cfg = self.cfg[self.name]
        super()._set_Wfactor()

        self.eta = cfg['eta']
        self.pr = cfg['pr_des']


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