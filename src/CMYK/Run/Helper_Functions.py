from CMYK.Object_Definitions.Base_Objects import Flow, GeometryInterface
import numpy as np

def T_T0(gamma, M):
    return (1 + (gamma-1)/2*M**2)**-1

def P_P0(gamma, M):
    return (1 + (gamma-1)/2*M**2)**(-gamma/(gamma-1))

def rho_rho0(gamma, M):
    return (1 + (gamma-1)/2*M**2)**(-1/(gamma-1))

def M_fromTT0(gamma, T, T0):
    return np.sqrt(((T/T0)**-1 - 1)*(2/gamma-1))

def M_fromPP0(gamma, P, P0):
    return np.sqrt(((P/P0)**(1-gamma) - 1)*(2/gamma-1))

def a(gamma, R, T):
    return np.sqrt(gamma * R * T)

def A_Astar(gamma, M):
    return ((gamma+1)/2) ** (-(gamma + 1)/(2*(gamma-1))) * ((1 + (gamma-1)/2*M**2) ** ((gamma + 1)/(2*(gamma-1)))) / M 