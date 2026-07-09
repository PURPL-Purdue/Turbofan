from CMYK.Object_Definitions.Base_Objects import ComponentBase

class Shaft(ComponentBase):

    def __init__(self, name):
        super().__init__(name, 'SHAFT')

        self.RPM = 0
        self.eta_mech = None
        self.generators = []    # List of power generators attached to the shaft i.e. turbines
        self.consumers = []     # List of power consumers attached to the shaft i.e. compressors, fans

    def config(self) -> None:
        cfg = self.cfg[self.name]
        self.eta_mech = cfg['eta_mech']

