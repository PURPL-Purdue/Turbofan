import yaml
from pathlib import Path
from CMYK.Object_Definitions.Base_Objects import ComponentBase

class AxialTurbine(ComponentBase):

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

        #-----------------------------------------------------
        #                    SHAFT OUTPUT
        #-----------------------------------------------------
        self.Shaft = None

    def config(self, configFile: Path) -> None:
        cfg = yaml.safe_load(configFile.read_text())[self.name]

        self.eta = cfg['eta']
    
    #-----------------------------------------------------
    #                   CMYK Methods
    #-----------------------------------------------------

    def CYAN(self):
        if self.name == "HPT":
            T0_out = ((1+self.engine.BURNER.FAR)*self.FlowIn.T0*self.FlowIn.Cp0 - self.engine.HPC.FlowIn.Cp0*(self.engine.HPC.FlowOut.T0-self.engine.HPC.FlowIn.T0)) / ((1+self.engine.BURNER.FAR)*self.FlowIn.Cp0)
        elif self.name == "LPT":
            T0_out = ((1+self.engine.BURNER.FAR)*self.FlowIn.T0*self.FlowIn.Cp0 - self.engine.LPC.FlowIn.Cp0*(self.engine.LPC.FlowOut.T0-self.engine.LPC.FlowIn.T0) - 
                                                           self.engine.FAN.bypass*self.engine.FAN.FlowIn.Cp0*(self.engine.FAN.FlowOut_COR.T0-self.engine.FAN.FlowIn.T0)) / ((1+self.engine.BURNER.FAR)*self.FlowIn.Cp0)
        else:
            raise RuntimeError("Invalid axial turbine name: Must be 'LPT' or 'HPT'")
        P0_out = self.FlowIn.P0*(1 - 1/self.eta*(1 - T0_out/self.FlowIn.T0))**(self.FlowIn.gammat/(self.FlowIn.gammat-1))

        self.FlowOut.setFlowTotalTP(T0_out, P0_out)

