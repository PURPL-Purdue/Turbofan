import yaml
from pathlib import Path
from CMYK.Object_Definitions.Base_Objects import ComponentBase

class Fan(ComponentBase):

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

    def config(self, configFile: Path) -> None:
        cfg = yaml.safe_load(configFile.read_text())[self.name]

        self.eta = cfg['eta']
        self.Pr  = cfg['Pr_Des']
        self.bypass = cfg['Bypass']

    #-----------------------------------------------------
    #                   CMYK Methods
    #-----------------------------------------------------

    def CYAN(self):
        T0_out = self.FlowIn.T0 * (1 + 1/self.eta*(self.Pr**((self.FlowIn.gammat-1)/self.FlowIn.gammat)-1))
        P0_out = self.FlowIn.P0 * self.Pr

        self.FlowOut_COR.setFlowTotalTP(T0_out, P0_out)
        self.FlowOut_BYP.setFlowTotalTP(T0_out, P0_out)
