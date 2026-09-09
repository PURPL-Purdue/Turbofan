"""
Engine Architecture
    - Front fan on LPS, driven by LPT.
    - Axial + Radial compressor on HPS, driven by HPT.
"""

from pathlib import Path

from CMYK.Object_Definitions.Components import (
    Turbofan, Start, Inlet, Fan, AxialCompressor,
    RadialCompressor, Burner, AxialTurbine,
    Nozzle, End, Shaft
)

from CMYK.Object_Definitions.Base_Objects import Display

CONFIG_PATH = Path(__file__).resolve().parent.parent/'Config_Files'/'Config_PURPL.yaml'
OUTPUT_PATH = Path(__file__).resolve().parent.parent/'Output'/'Output_PURPL.txt'

#----------------------------------------------------------------------------
#                       DECLARING ENGINE COMPONENTS
#----------------------------------------------------------------------------
AMB_FS  = Start('AMB_FS')
INLET   = Inlet('INLET')
FAN     = Fan('FAN')
NOZ_BYP = Nozzle('NOZ_BYP')
JET_BYP = End('JET_BYP')
HPCA    = AxialCompressor("HPCA")
HPCR    = RadialCompressor("HPCR")
BURNER  = Burner('BURNER')
HPT     = AxialTurbine('HPT')
LPT     = AxialTurbine('LPT')
NOZ_COR = Nozzle('NOZ_COR')
JET_COR = End('JET_COR')

LPS = Shaft('LPS')
HPS = Shaft('HPS')

#----------------------------------------------------------------------------
#                    ASSEMBLING AND CONFIGURING THE ENGINE
#----------------------------------------------------------------------------
Turbofan = Turbofan('Turbofan')

Turbofan.build(
    AMB_FS,
    INLET,
    FAN,
    NOZ_BYP,
    JET_BYP,
    HPCA,
    HPCR,
    BURNER,
    HPT,
    LPT,
    NOZ_COR,
    JET_COR,
    LPS, HPS
)

# CONFIG --------------------------------------------------------------------------
Turbofan.config(CONFIG_PATH)

#----------------------------------------------------------------------------
#                     LINKING AND CONFIGURING COMPONENTS
#----------------------------------------------------------------------------
Turbofan.interface(  "AMB_FS.FlowOut",        "INLET.FlowIn", "S1"  )
Turbofan.interface(   "INLET.FlowOut",          "FAN.FlowIn", "S2"  )
Turbofan.interface(     "FAN.FlowOut_BYP",  "NOZ_BYP.FlowIn", "S13" )
Turbofan.interface( "NOZ_BYP.FlowOut",      "JET_BYP.FlowIn", "S19" )
Turbofan.interface(     "FAN.FlowOut_COR",     "HPCA.FlowIn", "S21" )
Turbofan.interface(    "HPCA.FlowOut",         "HPCR.FlowIn", "S25" )
Turbofan.interface(    "HPCR.FlowOut",       "BURNER.FlowIn", "S3"  )
Turbofan.interface(  "BURNER.FlowOut",          "HPT.FlowIn", "S4"  )
Turbofan.interface(     "HPT.FlowOut",          "LPT.FlowIn", "S45" )
Turbofan.interface(     "LPT.FlowOut",      "NOZ_COR.FlowIn", "S5"  )
Turbofan.interface( "NOZ_COR.FlowOut",      "JET_COR.FlowIn", "S9"  )

# Low Pressure Spool Shaft Connections
Turbofan.interface( "FAN.Shaft", "LPS", "FAN_ShaftLink" )
Turbofan.interface( "LPT.Shaft", "LPS", "LPT_ShaftLink" )

# High Pressure Spool Shaft Connections
Turbofan.interface( "HPCA.Shaft", "HPS", "HPCA_ShaftLink" )
Turbofan.interface( "HPCR.Shaft", "HPS", "HPCR_ShaftLink" )
Turbofan.interface(  "HPT.Shaft", "HPS", "HPT_ShaftLink"  )

#----------------------------------------------------------------------------
#                             CYCLE ANALYSIS
#----------------------------------------------------------------------------
Turbofan.CYAN()

#----------------------------------------------------------------------------
#                                 OUTPUT
#----------------------------------------------------------------------------
Disp = Display(Turbofan)
Disp.textOutput(OUTPUT_PATH, verbose=True)

pass