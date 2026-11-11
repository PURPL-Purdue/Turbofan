"""
Engine Architecture
    - Front fan on LPS, driven by LPT.
    - Axial compressor + radial compressor on HPS, driven by HPT.
"""

from pathlib import Path

from CMYK.Object_Definitions.Components import (
    Turbofan, Start, Inlet, Fan, AxialCompressor,
    RadialCompressor, Burner, AxialTurbine,
    Nozzle, End, Shaft
)

from CMYK.Object_Definitions.Base_Objects import Display

CONFIG_PATH = Path(__file__).resolve().parent.parent/'Config_Files'/'Config_002.yaml'
OUTPUT_PATH = Path(__file__).resolve().parent.parent/'Output'/'Output_002.txt'

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
Turbofan.interface(  "HPT.Shaft", "HPS",  "HPT_ShaftLink" )


#----------------------------------------------------------------------------
#                             CYCLE ANALYSIS
#----------------------------------------------------------------------------

bypass_ratio = 0
calc_br = 0

Turbofan.CYAN()

# while bypass_ratio < 5 and abs(bypass_ratio - calc_br) > 0.01:
#     bypass_ratio += 0.01
#     Turbofan.FAN.bypass = bypass_ratio
#     Turbofan.CYAN()
#     amb_temp = 288.15
#
#     tau_f = Fan.T02 / amb_temp
#     tau_gamma = AxialTurbine.T0_1m / amb_temp
#     tau_c = AxialCompressor.Tr_total_actual * (RadialCompressor.T02 / AxialCompressor.T0_stages[-1])
#
#     calc_br = 1 / (tau_f - 1) * (tau_gamma - tau_c + 1 - tau_gamma / tau_c - 0.25 * (tau_f - 1))
#
# print(bypass_ratio)
#----------------------------------------------------------------------------
#                                 OUTPUT
#----------------------------------------------------------------------------
# Disp = Display(Turbofan)
# Disp.textOutput(OUTPUT_PATH, verbose=True)

# pass