import yaml
from pathlib import Path
from CMYK.Object_Definitions.Base_Objects import ComponentBase
import numpy as np

class Nozzle(ComponentBase):

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
    
    def config(self, configFile: Path) -> None:
        cfg = yaml.safe_load(configFile.read_text())[self.name]

        self.eta = cfg['eta']


    def calcExitVelocity(self) -> None:
        self.u_exit = np.sqrt(2*self.eta *(self.FlowIn.gamma /(self.FlowIn.gamma -1))*self.FlowIn.R*self.FlowIn.T0*(1 - (self.FlowOut.P/self.FlowIn.P0)**((self.FlowIn.gamma-1)/self.FlowIn.gamma)))

    #-----------------------------------------------------
    #                   CMYK Methods
    #-----------------------------------------------------

    def CYAN(self):
        self.FlowOut.copyFrom(self.FlowIn)

