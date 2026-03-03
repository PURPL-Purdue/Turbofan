import numpy as np

def T_T0(gamma, M):
    return (1 + (gamma-1)/2*M**2)**-1

def P_P0(gamma, M):
    return (1 + (gamma-1)/2*M**2)**(-gamma/(gamma-1))

def rho_rho0(gamma, M):
    return (1 + (gamma-1)/2*M**2)**(-1/(gamma-1))

def a(gamma, R, T):
    return np.sqrt(gamma * R * T)

def A_Astar(gamma, M):
    return ((gamma+1)/2) ** (-(gamma + 1)/(2*(gamma-1))) * ((1 + (gamma-1)/2*M**2) ** ((gamma + 1)/(2*(gamma-1)))) / M 

def sigXzweif(beta1, beta2):
    return abs((2*np.cos(beta2))/np.cos(beta1) * np.sin(beta1-beta2))