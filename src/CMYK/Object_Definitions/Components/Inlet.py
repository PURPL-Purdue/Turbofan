import yaml
from pathlib import Path
from CMYK.Object_Definitions.Base_Objects import ComponentBase
from CMYK.Run import Helper_Functions as HF

class Inlet(ComponentBase):

    def __init__(self, name):
        super().__init__(name, 'FLOWPATH')

        # INLET AND EXIT FLOWS --------------------------------
        self.FlowIn  = None
        self.FlowOut = None

        # INLET AND EXIT GEOMETRY INTERFACES ------------------
        self.GeoIn  = None
        self.GeoOut = None

    def config(self, configFile: Path) -> None:
        cfg = yaml.safe_load(configFile.read_text())[self.name]

        self.eta = cfg['eta']

    #-----------------------------------------------------
    #                   CMYK Methods
    #-----------------------------------------------------

    def CYAN(self):
        T0_out = self.FlowIn.T/HF.T_T0(self.FlowIn.gammat, self.FlowIn.M)
        P0_out = self.FlowIn.P*(1 + self.eta*(T0_out/self.FlowIn.T - 1))**(self.FlowIn.gammat/(self.FlowIn.gammat-1))

        self.FlowOut.setFlowTotalTP(T0_out, P0_out)