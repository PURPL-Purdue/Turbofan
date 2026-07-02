from CoolProp.CoolProp import PropsSI as CPP
from CMYK.Run import Helper_Functions as HF

class Flow:
    # Thermodynamic properties of interest
    def __init__(self, name):
        self.name: str = name

        self.T0: str | None = None
        self.P0: str | None = None

        self.T: str | None = None
        self.P: str | None = None

    def setFlowTotalTP(self, T0, P0):
        self.T0 = T0
        self.P0 = P0

        self.Cp0    = CPP( 'CPMASS', 'T', T0, 'P', P0, 'Air' )      # Total specific heat capacity at constant pressure     | J/kg/K
        self.Cv0    = CPP( 'CVMASS', 'T', T0, 'P', P0, 'Air' )      # Total specific heat capacity at constant volume       | J/kg/K
        self.gammat = self.Cp0/self.Cv0                             # Total specific heat ratio                             | nondim
        self.H0     = CPP( 'HMASS',  'T', T0, 'P', P0, 'Air' )      # Total enthalpy                                        | J/kg

        self.gamma = self.gammat                                    # Average gamma. Set to equal gammat because we don't know gammas

        self.R      = self.Cp0 * (self.gamma-1)/self.gamma          # Gas constant (no total/static distinction)            | J/kg/K
        self.S      = CPP( 'SMASS',  'T', T0, 'P', P0, 'Air' )      # Entropy (no total/static distinction)                 | J/kg/K

    def setFlowStaticTP(self, T, P):
        self.T = T
        self.P = P

        self.Cp     = CPP( 'CPMASS', 'T', T, 'P', P, 'Air' )        # Static specific heat capacity at constant pressure    | J/kg/K
        self.Cv     = CPP( 'CVMASS', 'T', T, 'P', P, 'Air' )        # Static specific heat capacity at constant volume      | J/kg/K
        self.gammas  = self.Cp/self.Cv                              # Static specific heat ratio                            | nondim
        self.H      = CPP( 'HMASS',  'T', T, 'P', P, 'Air' )        # Static enthalpy                                       | J/kg
        
        self.gamma = self.gammas                                    # Average gamma. Set to equal gammas because we don't know gammat

        self.R      = self.Cp * (self.gamma-1)/self.gamma           # Gas constant (no total/static distinction)            | J/kg/K
        self.S      = CPP( 'SMASS',  'T', T, 'P', P, 'Air' )        # Entropy (no total/static distinction)                 | J/kg/K
        self.A      = CPP('A', 'T', T, 'P', P, 'Air')


    def setFlowMach(self, M):
        if self.T0 is None and self.P0 is None and self.T is not None and self.P is not None:
            self.M = M
            self.T0 = self.T / HF.T_T0(self.gamma, M)
            self.P0 = self.P / HF.P_P0(self.gamma, M)
            self.setFlowTotalTP(self.T0, self.P0)
            self.gamma = (self.gammat + self.gammas)/2

        elif self.T0 is not None and self.P0 is not None and self.T is None and self.P is None:
            self.M = M
            self.T = HF.T_T0(self.gamma, M) * self.T0
            self.P = HF.P_P0(self.gamma, M) * self.P0
            self.setFlowStaticTP(self.T, self.P)
            self.gamma = (self.gammat + self.gammas)/2

        else:
            raise RuntimeError("Flow: total-static relationship overdefined. Perchance consider using calcMach()?")
    
    def calcMach(self):
        self.gamma = (self.gammat + self.gammas)/2
        self.M = HF.M_fromTT0(self.gamma, self.T, self.T0)


    def copyFrom(self, targetStation):
        self.__dict__.update({k: v for k, v in targetStation.__dict__.items() if k != 'name'})



