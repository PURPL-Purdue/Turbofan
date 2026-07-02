import yaml
from pathlib import Path
from CMYK.Object_Definitions.Base_Objects import ComponentBase

class RadialCompressor(ComponentBase):

    def __init__(self, name):
        super().__init__(name, 'FLOWPATH')

        # INLET AND EXIT FLOWS --------------------------------
        self.FlowIn  = None
        self.FlowOut = None

        # INLET AND EXIT GEOMETRY INTERFACES ------------------
        self.GeoIn  = None
        self.GeoOut = None

        # SHAFT CONNECTION ------------------------------------
        self.Shaft = None

    def config(self, configFile: Path) -> None:
        cfg = yaml.safe_load(configFile.read_text())[self.name]

        self.eta = cfg['eta']
        self.Pr = cfg['Pr_Des']

    #-----------------------------------------------------
    #                   CMYK Methods
    #-----------------------------------------------------

    def CYAN(self):
        T0_out = self.FlowIn.T0 * (1 + 1/self.eta*(self.Pr**((self.FlowIn.gammat-1)/self.FlowIn.gammat)-1))
        P0_out = self.FlowIn.P0 * self.Pr

        self.FlowOut.setFlowTotalTP(T0_out, P0_out)
    
    

