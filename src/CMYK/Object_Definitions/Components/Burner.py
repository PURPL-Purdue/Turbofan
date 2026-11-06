from typing import cast

from CoolProp.CoolProp import PropsSI
from CMYK.Object_Definitions.Base_Objects import ComponentBase
from Object_Definitions.Supplemental.Combustor import MAGENTA as mag
import cea

class Burner(ComponentBase):

    def __init__(self, name):
        super().__init__(name, 'FLOWPATH')

        # INLET AND EXIT FLOWS --------------------------------
        self.FlowIn  = None
        self.FlowOut = None

        # INLET AND EXIT GEOMETRY INTERFACES ------------------
        self.GeoIn  = None
        self.GeoOut = None

        # COMPONENT PROPERTIES --------------------------------
        self.eta = None
        self.LHV = None
        self.FAR = None
        self.T04 = None
        self.pr = None
        self.turbine_diameter = None # Diameter of the turbine for sizing purposes (m)

        self.Wfactor = None
        self.Wstream = None

    def config(self) -> None:
        cfg = self.cfg[self.name]
        super()._set_Wfactor()

        self.eta = cfg['eta']
        self.LHV = cfg['LHV']
        self.pr = cfg['pr_des']
        self.T04 = self.cfg['CYCLE']['T0_4']
        self.num_injectors = cfg['num_injectors']


    #-----------------------------------------------------
    #                   CMYK Methods
    #-----------------------------------------------------

    def CYAN(self):
        """Refer to CycleAnalysis.md for explanation of the math"""
        # PREPARING REQUIRED VALUES ---------------------
        h01 = self.FlowIn.h0
        P01 = self.FlowIn.P0
        eta = self.eta
        pr = self.pr
        LHV = self.LHV

        # T02 -------------------------------------------
        T02 = self.T04

        # P02 CALCULATION -------------------------------
        P02 = pr * P01

        # FAR CALCULATION -------------------------------
        h02 = PropsSI('HMASS', 'T', T02, 'P', P02, self.FlowIn.WF)      # TODO: Start from here, replacing working fluid with post-combustion mixture
        self.FAR = FAR = (h02 - h01) / (eta*LHV - h02)
        self.Wfactor += FAR

        # SET EXIT FLOW ---------------------------------
        self.FlowOut.setFlow(
            T0=T02, P0=P02, FAR=FAR,
            Wfactor=self.Wfactor, Wstream=self.Wstream
        )

    def MAGENTA(self):

        T3 = self.FlowIn.T
        P3 = self.FlowIn.P
        m = self.FlowIn.W
        turbine_size = self.turbine_diameter

        dp34 = (0.06 * P3) * 101325
        qref = dp34 / 20

        reference_area = mag.mm_aref_equation_1(T3, P3,dp34, qref,m)
        reference_diameter = mag.mm_dref_equation(reference_area)
        axial_length_ann = mag.mm_length_calculation(reference_diameter)

        combustor_area = 0.7 * reference_area
        combustor_diameter = 0.7 * reference_diameter

        outer_diameter_casing = mag.outer_diameter_reverse_flow(turbine_size, reference_area)
        outer_diameter_flame_tube = mag.outer_diameter_reverse_flow(turbine_size, combustor_area)

        with open ("combustor_geo_outputs", "w") as f:
            f.write(mag.format_values(outer_diameter_casing,axial_length_ann,reference_area))












