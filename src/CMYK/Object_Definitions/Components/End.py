
from CMYK.Object_Definitions.Base_Objects import ComponentBase


class End(ComponentBase):

    def __init__(self, name):
        super().__init__(name, 'FLOWPATH')

        # INLET FLOW AND GEOMETRY ------------------
        self.FlowIn = None
        self.GeoIn = None

        self.Wfactor = None
        self.Wstream = None

        # COMPONENT PROPERTIES --------------------
        self.u_out = None

    def config(self) -> None:
        pass

    def calc_exit_velocity(self):
        self.u_out = self.FlowIn.M * self.FlowIn.A

    # -----------------------------------------------------
    #                   CMYK Methods
    # -----------------------------------------------------

    def CYAN(self) -> None:
        self.Wfactor = self.FlowIn.Wfactor
        self.Wstream = self.FlowIn.Wstream
