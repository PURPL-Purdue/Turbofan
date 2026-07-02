import yaml
from pathlib import Path
from CMYK.Object_Definitions.Base_Objects import ComponentBase

class Ambient(ComponentBase):

    def __init__(self, name):
        super().__init__(name, 'FLOWPATH')
        
        # INLET AND EXIT FLOWS AND GEOMETRIES------------------
        # Logic to check if this is a starting or ending ambient
        if self.name[0:2] == 'FS':
            self.FlowOut = None
            self.GeoOut  = None
        else:
            self.FlowIn = None
            self.GeoIn  = None

    def config(self, config_file: Path) -> None:
        cfg = yaml.safe_load(config_file.read_text())['AMB']
        
        self.T  = cfg['T_0']
        self.P  = cfg['P_0']
        self.M_f = cfg['M_f']

    #-----------------------------------------------------
    #                   CMYK Methods
    #-----------------------------------------------------

    def CYAN(self) -> None:
        if self.name[-2:] == 'FS':
            self.FlowOut.setFlowStaticTP(self.T, self.P)    # Set static values using input T and P
            self.FlowOut.setFlowMach(self.M_f)              # Set total values using input M_f
        else:
            self.FlowIn.setFlowStaticTP(self.T, self.P)     # Set static values using input T and P
            self.FlowIn.calcMach()                          # Total values already known from flowpath, calculate exit Mach number