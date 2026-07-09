import numpy as np

def T_T0(gamma: float, M: float) -> float:
    """Calculates and returns T/T0 as per the isentropic state definition"""
    return (1 + (gamma-1)/2*M**2)**-1

def P_P0(gamma: float, M: float) -> float:
    """Calculates and returns P/P0 as per the isentropic state definition"""
    return (1 + (gamma-1)/2*M**2)**(-gamma/(gamma-1))

def rho_rho0(gamma: float, M: float) -> float:
    """Calculates and returns rho/rho0 as per the isentropic state definition"""
    return (1 + (gamma-1)/2*M**2)**(-1/(gamma-1))

def M_fromTT0(gamma: float, T: float, T0: float) -> float:
    """Calculates and returns Mach number from inputting T and T0 using the isentropic definition of T/T0"""
    return np.sqrt(((T/T0)**-1 - 1)*(2/(gamma-1)))

def M_fromPP0(gamma: float, P: float, P0: float) -> float:
    """Calculates and returns Mach number from inputting P and P0 using the isentropic definition of P/P0"""
    return np.sqrt(((P/P0)**(1-gamma) - 1)*(2/(gamma-1)))

def a(gamma: float, R: float, T: float) -> float:
    """Calculates and returns the local speed of sound"""
    return np.sqrt(gamma * R * T)

def T02_T01_from_P02_P01(gamma: float, P02: float, P01: float) -> float:
    """Calculates temperature ratio from pressure ratio using isentropic relations"""
    return (P02/P01)**((gamma-1)/gamma)

def P02_P01_from_T02_T01(gamma: float, T02: float, T01: float) -> float:
    """Calculates pressure ratio from temperature ratio using isentropic relations"""
    return (T02/T01)**(gamma/(gamma-1))

def A_Astar(gamma: float, M: float) -> float:
    """Calculates and returns A/Astar as per the isentropic state definition"""
    return ((gamma+1)/2) ** (-(gamma + 1)/(2*(gamma-1))) * ((1 + (gamma-1)/2*M**2) ** ((gamma + 1)/(2*(gamma-1)))) / M