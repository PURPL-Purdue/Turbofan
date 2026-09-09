from CMYK.Object_Definitions.Base_Objects import ComponentBase

class Start(ComponentBase):

    def __init__(self, name):
        super().__init__(name, 'FLOWPATH')

        # EXIT FLOW AND GEOMETRY ------------------
        self.FlowOut = None
        self.GeoOut = None

        # COMPONENT PROPERTIES ----------------------
        self.T = None
        self.P = None
        self.M_f = None

        self.Wfactor = None
        self.Wstream = None

        self.u_in = None

    def config(self) -> None:
        cfg = self.cfg[self.name]
        super()._set_Wfactor()

        self.T = cfg['T_0']
        self.P = cfg['P_0']
        self.M_f = cfg['M_f']

    def calc_inlet_velocity(self):
        self.u_in = self.FlowOut.M * self.FlowOut.A

    # -----------------------------------------------------
    #                   CMYK Methods
    # -----------------------------------------------------

    def CYAN(self) -> None:
        self.FlowOut.setFlow(
            T=self.T, P=self.P, M=self.M_f,
            Wfactor=self.Wfactor, Wstream=self.Wstream
        )  # It's ambient! There's literally nothing to do lol.