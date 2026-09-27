from CoolProp.CoolProp import PropsSI
from CMYK.Run import helper_functions as hf
from .VelocityTriangle import VelocityTriangle

class Flow:
    def __init__(self, name: str) -> None:
        self.name: str = name

        self.VT = VelocityTriangle()

        self.WF = None          # Working fluid
        self.FAR = None         # Fuel-to-air ratio (mass-based)                        | kg_fuel/kg_air

        self.T0 = None          # Total temperature                                     | K
        self.P0 = None          # Total pressure                                        | Pa
        self.T = None           # Static temperature                                    | T
        self.P = None           # Static pressure                                       | Pa
        self.M = None           # Mach number                                           | nondim

        self.h0 = None          # Total enthalpy                                        | J/kg
        self.h  = None          # Static enthalpy                                       | J/kg

        self.gamma0     = None  # Total specific heat ratio                             | nondim
        self.Cp0        = None  # Total specific heat capacity at constant pressure     | J/kg/K
        self.Cv0        = None  # Total specific heat capacity at constant volume       | J/kg/K
        self.gamma      = None  # Static specific heat ratio                            | nondim
        self.Cp         = None  # Static specific heat capacity at constant pressure    | J/kg/K
        self.Cv         = None  # Static specific heat capacity at constant volume      | J/kg/K
        self.gamma_avg  = None  # Average gamma_avg                                     | nondim

        self.R = None           # Gas constant (no total/static distinction)            | J/kg/K
        self.s = None           # Entropy (no total/static distinction)                 | J/kg/K
        self.A = None           # Speed of sound (based on static temperature)          | m/s

        self.totally_defined = False        # Flag for whether total properties are known or not
        self.statically_defined = False     # Flag for whether static properties are known or not

        self.W = None                       # Mass flow rate
        self.Wfactor = None
        self.Wstream = None

    def setFlow(self, working_fluid: str = 'Air', FAR: float = 0, Wfactor: float = -9999, Wstream: str = 'N/A', **kwargs: float) -> None:
        """
        Sets flow thermodynamic properties.

        The working fluid must be specified first, and will be assumed to be air if not specified. The intention for letting the user specify the working fluid is to allow for changes in composition after combustion occurs

        Two independent, intensive properties must be provided. Optionally, a Mach number may also be provided.

        If a Mach number is not provided, only half (total or static) of the thermodynamic state can be initially specified depending on what other arguments are passed. If the remaining half of the state is already populated in the flow state, the Mach number will be (re)calculated, overriding the existing mach number if it exists.

        If a Mach number is provided in addition to the two independent intensive properties, the entire thermodynamic state will be defined, with the existing state overwritten entirely.

        If ONLY a Mach number is provided AND the state is currently only half defined, the rest of the state will be set.

        A fuel-to-air ratio, FAR, may also be specified. If provided, the current existing/Nonetype will be overwritten with the new value. If not provided, the current existing/Nonetype will be overridden with a value of zero.

        Currently allowed pairs of properties:
            - T0, P0
            - T, P

        Example:
            setFlow('Air', T0 = 303, P0 = 101300, M = 0.5)
        The above method call will set the Flow object's working fluid to be regular air and will set the full thermodynamic state of the air. The flow state's fuel-to-air ratio is now zero, regardless of its previous state.
        using total temperature T0, total pressure P0, and Mach number M.
        """
        self.Wfactor = Wfactor if Wfactor != -9999 else self.Wfactor
        self.Wstream = Wstream if Wstream != 'N/A' else self.Wstream
        self.WF = working_fluid
        self.FAR = FAR if self.FAR !=0 else self.FAR # TODO: Check this line??? What is it doing???

        # INPUT VALIDATION -------------------------------------------------------------------------------------------------------------------------------
        ALLOWED_PROPERTIES = {'T0', 'P0', 'h0', 'T', 'P', 'h', 's'}
        if len(kwargs) == 0:
            raise RuntimeError("what are you doing lol")
        elif len(kwargs) == 1:
            # Continue with one input only if the one input is Mach number
            if 'M' not in set(kwargs.keys()):
                raise RuntimeError("Flow: underdefined thermodynamic state. Unless you are providing Mach number by itself, two independent, intensive properties must be provided.")
        elif len(kwargs) == 2:
            # Continue only if both provided inputs are valid
            if not set(kwargs.keys()).issubset(ALLOWED_PROPERTIES):
                raise RuntimeError("Flow: one or more of the two provided properties are invalid")
        elif len(kwargs)  == 3:
            # Allow through the case where two independent, intensive properties are provided, and a Mach number is specified to relate total and static conditions
            if not ('M' in set(kwargs.keys()) and set(kwargs.keys()).difference({'M'}).issubset(ALLOWED_PROPERTIES)):
                raise RuntimeError("Flow: overdefined thermodynamic state. Two independent, intensive properties must be provided.")
        elif len(kwargs) >= 4:
            raise RuntimeError("Flow: overdefined thermodynamic state. Two independent, intensive properties must be provided.")

        # SET FLOW STATE ------------------------------------------------------------------------------------------------------------------------------------
        # At this point, the only two cases that could have made it here are 1) two valid properties or 2) two valid properties and a Mach number
        prop1 = None
        prop2 = None
        if len(kwargs) == 1:
            self.setFlowMach(kwargs['M'])
        elif len(kwargs) == 3:
            prop1 = list(set(kwargs.keys()).difference({'M'}))[0]
            prop2 = list(set(kwargs.keys()).difference({'M'}))[1]
        else:
            prop1 = list(kwargs.keys())[0]
            prop2 = list(kwargs.keys())[1]

        self.R = PropsSI('GAS_CONSTANT', working_fluid) / PropsSI('MOLAR_MASS', working_fluid)

        if {prop1, prop2} == {'T0', 'P0'}:
            self.setFlowTotalTP(kwargs['T0'], kwargs['P0'])
            if len(kwargs) == 3:
                self.setFlowMach(kwargs['M'])
            elif self.statically_defined:
                self.calcMach()
        elif {prop1, prop2} == {'T', 'P'}:
            self.setFlowStaticTP(kwargs['T'], kwargs['P'])
            if len(kwargs) == 3:
                self.setFlowMach(kwargs['M'])
            if self.totally_defined:
                self.calcMach()

    def setFlowTotalTP(self, T0: float, P0: float) -> None:
        self.T0 = T0
        self.P0 = P0

        self.h0     = PropsSI('HMASS', 'T', T0, 'P', P0, self.WF)

        self.Cp0    = PropsSI('CPMASS', 'T', T0, 'P', P0, self.WF)
        self.Cv0    = PropsSI('CVMASS', 'T', T0, 'P', P0, self.WF)
        self.gamma0 = self.Cp0 / self.Cv0

        self.s      = PropsSI('SMASS', 'T', T0, 'P', P0, self.WF)

        self.totally_defined = True

    def setFlowStaticTP(self, T: float, P: float) -> None:
        self.T = T
        self.P = P

        self.h      = PropsSI('HMASS', 'T', T, 'P', P, self.WF)

        self.Cp     = PropsSI('CPMASS', 'T', T, 'P', P, self.WF)
        self.Cv     = PropsSI('CVMASS', 'T', T, 'P', P, self.WF)
        self.gamma  = self.Cp / self.Cv

        self.s      = PropsSI('SMASS', 'T', T, 'P', P, self.WF)
        self.A      = PropsSI('A', 'T', T, 'P', P, self.WF)

        self.statically_defined = True

    def setFlowMach(self, M: float) -> None:
        """
        Takes the known half of the thermodynamic state and applies the Mach number input to calculate the other unknown half. Includes an additional layer of checking to make sure that the user isn't overdefining the thermodynamic state
        """
        if self.T0 is None and self.P0 is None and self.T is not None and self.P is not None:
            self.M = M
            self.T0 = self.T / hf.T_T0(self.gamma, M)
            self.P0 = self.P / hf.P_P0(self.gamma, M)
            self.setFlowTotalTP(self.T0, self.P0)
            self.gamma_avg = (self.gamma0 + self.gamma) / 2

        elif self.T0 is not None and self.P0 is not None and self.T is None and self.P is None:
            self.M = M
            # TODO: KNOWN INACCURACY: When using isentropic relations, static gamma should be used. However, in situations where setFlowMach is called and only T0 and P0 are known, only total gamma is known, which is what we end up having to use. A iterative method could be implemented to converge on a solution, though that is rather :skull:
            self.T = hf.T_T0(self.gamma0, M) * self.T0
            self.P = hf.P_P0(self.gamma0, M) * self.P0
            self.setFlowStaticTP(self.T, self.P)
            self.gamma_avg = (self.gamma0 + self.gamma) / 2

        else:
            raise RuntimeError("Flow: total-static relationship overdefined. Perchance consider using calcMach()?")

    def calcMach(self) -> None:
        self.gamma_avg = (self.gamma0 + self.gamma) / 2
        self.M = hf.M_fromTT0(self.gamma, self.T, self.T0)

    def copyFrom(self, target_station: Flow) -> None:
        self.__dict__.update({k: v for k, v in target_station.__dict__.items() if k != 'name'})



