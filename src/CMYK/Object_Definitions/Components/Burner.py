from CoolProp.CoolProp import PropsSI
from CMYK.Object_Definitions.Base_Objects import ComponentBase
from pyfluids import Mixture, FluidsList, Input
from Python.Combustor.CEA import CEA_Wrap as CEA

class Burner(ComponentBase):

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
        self.LHV = None
        self.FAR = None
        self.T04 = None
        self.pr = None

        self.Wfactor = None
        self.Wstream = None

    def config(self) -> None:
        cfg = self.cfg[self.name]
        super()._set_Wfactor()

        self.eta = cfg['eta']
        self.LHV = cfg['LHV']
        self.pr = cfg['Pr_Des']
        self.T04 = self.cfg['CYCLE']['T0_4']


    #-----------------------------------------------------
    #                   CMYK Methods
    #-----------------------------------------------------

    def CYAN(self):
        """Refer to CycleAnalysis.md for explanation of the math"""
        # PREPARING REQUIRED VALUES ---------------------
        h01 = self.FlowIn.h0
        P01 = self.FlowIn.P0
        eta = self.eta
        pr = self.pr
        LHV = self.LHV

        # T02 -------------------------------------------
        T02 = self.T04

        # P02 CALCULATION -------------------------------
        P02 = pr * P01

        # FAR CALCULATION -------------------------------
        h02 = PropsSI('HMASS', 'T', T02, 'P', P02, self.FlowIn.WF)      # TODO: Start from here, replacing working fluid with post-combustion mixture
        self.FAR = FAR = (h02 - h01) / (eta*LHV - h02)
        self.Wfactor += FAR

        # SET EXIT FLOW ---------------------------------
        self.FlowOut.setFlow(
            T0=T02, P0=P02, FAR=FAR,
            Wfactor=self.Wfactor, Wstream=self.Wstream
        )

    def CEA_run(self, phi, fuel, oxid):
        """Run CEA and return the results"""
        problem = CEA.HPProblem(pressure = (self.FlowIn.P0 / 100), massf = True, pressure_units = "bar")
        problem.set_phi(phi)
        data = problem.run(fuel, oxid)

        spec = []
        values = []

        for element in sorted(data.prod_c):
            spec.append(element)
            values.append(data.prod_c[element])

        pairs = sorted(zip(values, spec), reverse=True)

        pres = data.p
        temp = data.t

        return pairs, pres, temp