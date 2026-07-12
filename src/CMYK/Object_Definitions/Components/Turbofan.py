from pathlib import Path
from pint import UnitRegistry

from CMYK.Object_Definitions.Base_Objects import Engine, Compressor, Flow
from .Start import Start
from .Burner import Burner
from .End import End
from CMYK.Object_Definitions.Components.Shaft import Shaft

DEBUG_PATH = Path(__file__).resolve().parent.parent.parent /'Output'/'Debug.txt'
UR = UnitRegistry()

class Turbofan(Engine):
    def __init__(self, name):
        super().__init__(name)
        self.specific_thrust_total = None
        self.specific_thrust_core = None
        self.specific_thrust_bypass = None

        self.Wtotal = None
        self.Wcore = None
        self.Wbypass = None
        self.Wfuel = None

        self.total_thrust = None
        self.core_thrust = None
        self.bypass_thrust = None
        self.Fbypass_Fcore = None

        self.OPR = None
        self.delta_KE = None
        self.thermal_power = None

        self.thermal_eff = None
        self.propulsive_eff = None
        self.total_eff = None
        self.TSFC = None

        self.FAR = None
        self.LHV = None
        self.bypass = None
        self.total_design_thrust = None

    # ----------------------------------------------------------------------------
    #                         PERFORMANCE CALCULATIONS
    # ----------------------------------------------------------------------------

    def performance(self):
        self.pull_attributes()
        self.calc_velocities()
        self.calc_specific_thrusts()
        self.calc_mass_flows()
        self.calc_thrusts()
        self.calc_efficiencies()
        self.calc_OPR()

    def pull_attributes(self):
        # TODO: Pulls attributes up from components to the engine level for use in calculating performance parameters
        burnerCounter = 0
        for attributeValue in self.__dict__.values():
            if isinstance(attributeValue, Burner):
                if burnerCounter != 0:
                    raise RuntimeError("Multiple burners found!")
                burnerCounter += 1
                self.FAR = attributeValue.FAR
                self.LHV = attributeValue.LHV

        self.bypass = self.cfg['FAN']['Bypass']
        self.total_design_thrust = (self.cfg['CYCLE']['design_thrust'] * UR.lbf).to(UR.N).magnitude

    def calc_velocities(self):
        for attributeValue in self.__dict__.values():
            if isinstance(attributeValue, Start):
                attributeValue.calc_inlet_velocity()
            if isinstance(attributeValue, End):
                attributeValue.calc_exit_velocity()

    def calc_specific_thrusts(self):
        """Specific thrust calculated specific to core mass flow rate. Use total thrust target with normal specific thrust to get core mass flow rate"""
        self.specific_thrust_core = 0
        self.specific_thrust_bypass = 0

        for attributeValue in self.__dict__.values():
            if isinstance(attributeValue, Start):
                inlet = attributeValue

                if inlet.Wstream == 'FULL':
                    self.specific_thrust_core -= 1.0 * inlet.u_in
                    self.specific_thrust_bypass -= (inlet.Wfactor - 1) * inlet.u_in
                elif inlet.Wstream == 'CORE':
                    self.specific_thrust_core -= inlet.Wfactor * inlet.u_in
                elif inlet.Wstream == 'BYPASS':
                    self.specific_thrust_bypass -= inlet.Wfactor * inlet.u_in

            if isinstance(attributeValue, End):
                outlet = attributeValue

                if outlet.Wstream == 'CORE':
                    self.specific_thrust_core += outlet.Wfactor * outlet.u_out
                elif outlet.Wstream == 'BYPASS':
                    self.specific_thrust_bypass += outlet.Wfactor * outlet.u_out

        self.specific_thrust_total = self.specific_thrust_core + self.specific_thrust_bypass

    def calc_mass_flows(self):
        self.Wcore = self.total_design_thrust/self.specific_thrust_total
        self.Wbypass = self.Wcore * self.bypass
        self.Wtotal = self.Wcore + self.Wbypass
        self.Wfuel = self.Wcore * self.FAR

        self.set_mass_flows()

    def set_mass_flows(self):
        for compName, compObj in self.flowpath.items():
            for flowName, flowObj in vars(compObj).items():
                if isinstance(flowObj, Flow):
                    flowObj.W = flowObj.Wfactor * self.Wcore
                if isinstance(flowObj, Shaft):
                    flowObj.required_power = flowObj.specific_required_power * self.Wcore

    def calc_thrusts(self):
        self.total_thrust = self.Wcore * self.specific_thrust_total
        self.core_thrust = self.Wcore * self.specific_thrust_core
        self.bypass_thrust = self.Wcore * self.specific_thrust_bypass
        self.Fbypass_Fcore = self.bypass_thrust/self.core_thrust

    def calc_efficiencies(self):
        # THERMAL EFFICIENCY ---------------------------------------------------
        self.delta_KE = 0
        u_in = -9999
        for attributeValue in self.__dict__.values():

            if isinstance(attributeValue, Start):
                inlet = attributeValue
                self.delta_KE -= inlet.Wfactor * self.Wcore * (inlet.u_in ** 2)
                u_in = inlet.u_in

            if isinstance(attributeValue, End):
                outlet = attributeValue
                self.delta_KE += outlet.Wfactor * self.Wcore * (outlet.u_out ** 2)

        if self.FAR is None or self.LHV is None or u_in == -9999:
            raise RuntimeError("Assignment error: either FAR, LHV, or u_in was not assigned a value.")
        self.thermal_power = self.FAR * self.Wcore * self.LHV

        self.thermal_eff = 0.5*self.delta_KE/self.thermal_power


        # PROPULSIVE EFFICIENCY ----------------------------------------------
        self.propulsive_eff = self.total_thrust*u_in/self.delta_KE

        # TOTAL EFFICIENCY ----------------------------------------------
        self.total_eff = self.thermal_eff * self.propulsive_eff

        # TSFC ---------------------------------------------------------------
        self.TSFC = self.FAR/self.specific_thrust_total

    def calc_OPR(self):
        self.OPR = 1

        for attributeValue in self.__dict__.values():
            if isinstance(attributeValue, Compressor):
                self.OPR *= attributeValue.pr