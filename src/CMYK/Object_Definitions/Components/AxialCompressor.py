from CMYK.Object_Definitions.Base_Objects import Flow
from CMYK.Object_Definitions.Base_Objects import GeometryInterface

class AxialCompressor:

    #-----------------------------------------------------
    #            Flow Flow Inlets and Exits
    #-----------------------------------------------------
    FlowIn = Flow()
    FlowOut = Flow()

    #-----------------------------------------------------
    #          Inlet and Exit Geometry Interfaces
    #-----------------------------------------------------
    GeoIn = GeometryInterface(
        type = "ANNULAR"
    )
    GeoOut = GeometryInterface(
        type = "ANNULAR"
    )

    #-----------------------------------------------------
    #                   CMYK Methods
    #-----------------------------------------------------
    # eta = 




    # def CYAN():
    #     T0_25 = T0_2*(1 + 1/eta.cLP*(Pr.cLP**((gamma.cLP-1)/gamma.cLP)-1))
    #     P0_25 = P0_2*Pr.cLP

