import yaml
from pathlib import Path
from CMYK.Object_Definitions.Base_Objects import ComponentBase

class AxialCompressor(ComponentBase):

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

    def config(self, config_file: Path) -> None:
        cfg = yaml.safe_load(config_file.read_text())[self.name]

        self.eta = cfg['eta']
        self.Pr = cfg['Pr_Des']

    #-----------------------------------------------------
    #                   CMYK Methods
    #-----------------------------------------------------

    def cyan(self):
        T0_out = self.FlowIn.T0 * (1 + 1/self.eta*(self.Pr**((self.FlowIn.gammat-1)/self.FlowIn.gammat)-1))
        P0_out = self.FlowIn.P0 * self.Pr

        self.FlowOut.setFlowTotalTP(T0_out, P0_out)

    #-----------------------------------------------------
    #                   General Methods
    #-----------------------------------------------------
    def createCascades(self, sequence):
        ''' USAGE NOTES:
        The "sequence" parameter defines a sequence of rotors and stators. The syntax of
        the sequence string must strictly adhere to the outlined convention with the letters
        'R' (for rotor) and 'S' (for stator) connected with an '>' as shown:
            R>S>R>S>R>S
        Inlet/exit guide vanes are treated as regular stators when setting up the cascade and
        should also be specified as an S:
            S>R>S>R>S
        '''
        sequence = sequence.split('>')
        for row in sequence:
            if (row == 'R'):
                pass
                