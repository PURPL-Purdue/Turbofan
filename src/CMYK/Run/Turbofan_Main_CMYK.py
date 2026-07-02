"""
   .............................................................................................................................................
   ::'#######::'##:::'##:'#######::'#######::'##::::::::::::::'########:'##:::'##:'#######::'#######:::'######::'########:::'###::::'##::: ##:::
   :: ##... ##: ##::: ##: ##... ##: ##... ##: ##::::::::::::::... ##..:: ##::: ##: ##... ##: ##... ##:'##... ##: ##.....:::'## ##::: ###:: ##:::
   :: ##::: ##: ##::: ##: ##::: ##: ##::: ##: ##::::::::::::::::: ##:::: ##::: ##: ##::: ##: ##::: ##: ##::: ##: ##:::::::'##:. ##:: ####: ##:::
   :: #######:: ##::: ##: #######:: #######:: ##::::::::::::::::: ##:::: ##::: ##: #######:: #######:: ##::: ##: #######:'##:::. ##: ## ## ##:::
   :: ##....::: ##::: ##: ##. ##::: ##....::: ##::::::::::::::::: ##:::: ##::: ##: ##. ##::: ##... ##: ##::: ##: ##.....: #########: ##. ####:::
   :: ##::::::: ##::: ##: ##:. ##:: ##::::::: ##::::::::::::::::: ##:::: ##::: ##: ##:. ##:: ##::: ##: ##::: ##: ##:::::: ##.... ##: ##:. ###:::
   :: ##:::::::. ######:: ##::. ##: ##::::::: ########::::::::::: ##::::. ######:: ##::. ##: #######::. ######:: ##:::::: ##:::: ##: ##::. ##:::
   ::..:::::::::......:::..::::..::..::::::::........::::::::::::..::::::......:::..::::..::..::::..:::......:::..:::::::..:::::..::..::::..::::

TODO: redo the burner cycle analysis to make FAR a design input
TODO: reconfirm all the cycle analysis equations based on 490 HWs
"""


from pathlib import Path

from CMYK.Object_Definitions.Components import (
    Ambient, Inlet, Fan, AxialCompressor,
    RadialCompressor, Burner, AxialTurbine,
    Nozzle, Shaft
)

from CMYK.Object_Definitions.Base_Objects import Engine, Display

CONFIG_PATH = Path(__file__).resolve().parent.parent/'Config_Files'/'Config.yaml'
OUTPUT_PATH = Path(__file__).resolve().parent.parent/'Output'/'Output.txt'

#----------------------------------------------------------------------------
#                       DECLARING ENGINE COMPONENTS
#----------------------------------------------------------------------------
AMB_FS  = Ambient('AMB_FS')
INLET   = Inlet('INLET')
FAN     = Fan('FAN')
NOZ_BYP = Nozzle('NOZ_BYP')
AMB_BYP = Ambient('AMB_BYP')
LPC     = AxialCompressor("LPC")
HPC     = RadialCompressor("HPC")
BURNER  = Burner('BURNER')
HPT     = AxialTurbine('HPT')
LPT     = AxialTurbine('LPT')
NOZ_COR = Nozzle('NOZ_COR')
AMB_COR = Ambient('AMB_COR')

LPS = Shaft('LPS')
HPS = Shaft('HPS')

#----------------------------------------------------------------------------
#                          ASSEMBLING THE ENGINE
#----------------------------------------------------------------------------
Turbofan = Engine('Turbofan')

Turbofan.build(
    AMB_FS,  INLET,   FAN,
    NOZ_BYP, AMB_BYP, LPC,
    HPC,     BURNER,  HPT, 
    LPT,     NOZ_COR, AMB_COR,
    LPS, HPS
)

Turbofan.config(CONFIG_PATH)

#----------------------------------------------------------------------------
#                           LINKING COMPONENTS
#----------------------------------------------------------------------------
Turbofan.interface(  "AMB_FS.FlowOut",        "INLET.FlowIn", "S1"  )
Turbofan.interface(   "INLET.FlowOut",          "FAN.FlowIn", "S2"  )
Turbofan.interface(     "FAN.FlowOut_BYP",  "NOZ_BYP.FlowIn", "S13" )
Turbofan.interface( "NOZ_BYP.FlowOut",      "AMB_BYP.FlowIn", "S19" )
Turbofan.interface(     "FAN.FlowOut_COR",      "LPC.FlowIn", "S21" )
Turbofan.interface(     "LPC.FlowOut",          "HPC.FlowIn", "S25" )
Turbofan.interface(     "HPC.FlowOut",       "BURNER.FlowIn", "S3"  )
Turbofan.interface(  "BURNER.FlowOut",          "HPT.FlowIn", "S4"  )
Turbofan.interface(     "HPT.FlowOut",          "LPT.FlowIn", "S45" )
Turbofan.interface(     "LPT.FlowOut",      "NOZ_COR.FlowIn", "S5"  )
Turbofan.interface( "NOZ_COR.FlowOut",      "AMB_COR.FlowIn", "S9"  )

# Low Pressure Spool Shaft Connections
Turbofan.interface( "FAN.Shaft", "LPS", "FAN_ShaftLink" )
Turbofan.interface( "LPC.Shaft", "LPS", "LPC_ShaftLink" )
Turbofan.interface( "LPT.Shaft", "LPS", "LPT_ShaftLink" )

# High Pressure Spool Shaft Connections
Turbofan.interface( "HPC.Shaft", "HPS", "HPC_ShaftLink" )
Turbofan.interface( "HPT.Shaft", "HPS", "HPT_ShaftLink" )


#----------------------------------------------------------------------------
#                           CYCLE ANALYSIS CONFIG
#----------------------------------------------------------------------------

Turbofan.CYAN()

Disp = Display(Turbofan)
Disp.textOutput(OUTPUT_PATH)
Disp.plotOutput()

pass