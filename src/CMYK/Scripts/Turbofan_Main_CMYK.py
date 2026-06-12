import sys
from pathlib import Path

# Call back to the parent "src" folder and add the whole folder to python's search path. This will allow us to import components
src_path = str(Path(__file__).resolve().parent.parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from CMYK.Object_Definitions.Components.AxialCompressor import AxialCompressor

# LPCconfig = 'CMYK/Config_Files/compressorConfigTemplate.yaml'

# LPC = Component(LPCconfig)





#----------------------------------------------------------------------------
#                       DECLARING ENGINE COMPONENTS
#----------------------------------------------------------------------------
Freestream = Freestream()
Inlet = Inlet()
Fan = Fan()
LPC = AxialCompressor()
HPC = RadialCompressor()
Burner = Burner()
HPT = AxialTurbine()
LPT = AxialTurbine()
Nozzle = Nozzle()
Ambient = Ambient()

#----------------------------------------------------------------------------
#                    CONFIGURING ENGINE CYCLE PROPERTIES
#----------------------------------------------------------------------------
