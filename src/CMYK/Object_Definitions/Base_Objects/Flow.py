from CoolProp.CoolProp import PropsSI

class Flow:
    # Thermodynamic properties of interest
    Pt : float      # Pa
    P  : float      # Pa
    Tt : float      # K
    T  : float      # K
    MN : float      # nondim

    R     = PropsSI('GAS_CONSTANT', 'Air') / PropsSI('MOLAR_MASS', 'Air')   # J/kg/K
    Cp    = PropsSI('CPMASS', 'Air')                                        # J/kg/K
    Cv    = PropsSI('CVMASS', 'Air')                                        # J/kg/K
    gamma = Cp/Cv                                                           # nondim

    def setTotalTP(self, Tt, Pt, MN):
        self.Tt = Tt
        self.Pt = Pt
        self.MN = MN

        self.T = TqTt(self.gamma, MN) * self.Tt
        self.P = PqPt(self.gamma, MN) * self.Pt

    def setStaticTP(self, T, P, MN):
        self.T = T
        self.P = P
        self.MN = MN

        self.Tt = T / TqTt(self.gamma, MN)
        self.Pt = P / PqPt(self.gamma, MN)






def TqTt(gamma, M):
    return (1 + (gamma-1)/2*M**2)**-1

def PqPt(gamma, M):
    return (1 + (gamma-1)/2*M**2)**(-gamma/(gamma-1))