import yaml
from pathlib import Path
from CMYK.Object_Definitions.Base_Objects import ComponentBase

class Burner(ComponentBase):

    def __init__(self, name):
        super().__init__(name, 'FLOWPATH')

        # INLET AND EXIT FLOWS --------------------------------
        self.FlowIn  = None
        self.FlowOut = None

        # INLET AND EXIT GEOMETRY INTERFACES ------------------
        self.GeoIn  = None
        self.GeoOut = None
    
    def config(self, configFile: Path) -> None:
        cfg       = yaml.safe_load(configFile.read_text())[self.name]
        cfg_cycle = yaml.safe_load(configFile.read_text())['CYCLE']

        self.eta = cfg['eta']
        self.LHV = cfg['LHV']
        # self.FAR = cfg['FAR']
        self.Pr = cfg['Pr_Des']
        self.T0_4 = cfg_cycle['T0_4']

    #-----------------------------------------------------
    #                   CMYK Methods
    #-----------------------------------------------------

    def CYAN(self):
        T0_out = self.T0_4
        P0_out = self.FlowIn.P0 * self.Pr

        self.FAR = (T0_out/self.FlowIn.T0 - 1)/((self.eta*self.LHV)/(self.FlowIn.Cp0*self.FlowIn.T0)-T0_out/self.FlowIn.T0)

        self.FlowOut.setFlowTotalTP(T0_out, P0_out)