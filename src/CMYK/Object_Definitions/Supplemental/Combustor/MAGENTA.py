import math
import numpy as np


def mm_aref_equation_1(p3, t3, dp34, qref, m):
    """
    Malconian and Modak Equation 1 for calculating reference area
    :param p3: Stagnation pressure at combustor inlet (Pa)
    :param t3: Stagnation temperature at combustor inlet (K)
    :param dp34: Overall total pressure loss from 3-4 (Pa)
    :param qref: Reference dynamic pressure (Pa)
    :param m: Mass flow rate (kg/s)
    :return: Reference Area (m^2)
    """
    k = 143.5
    calculation = (k * (((m * math.sqrt(t3)) / p3) ** 2) * ((dp34 / qref) / (dp34 / p3))) ** 0.5
    return calculation

def mm_dref_equation(aref):
    """
    Malconian and Modak Equation 2 for calculating diameter of combustor
    :param aref: Reference area (m^2)
    :return: Reference Diameter (m)
    """
    calculation = math.sqrt((4 * aref) / math.pi)
    return calculation

def mm_aref_equation_2(theta, m, p3, t3, b):
    """
    Malconian and Modak Equation 2 for calculating reference area
    :param theta: Theta parameter (kg^(3/4)m * s^(-3.5)
    :param m: Mass flow rate (kg/s)
    :param p3: Stagnation pressure at combustor inlet (Pa)
    :param t3: Stagnation temperature at combustor inlet (K)
    :param b: Inlet Temperature factor (K) [Find using equations in M&M]
    :return: Reference Area (m^2)
    """
    calculation = ((math.pi / 4) ** (3 / 11)) * (((theta * m) / ((p3 ** 1.75) * math.exp(t3 / b))) ** (8 / 11))
    return calculation

def mm_theta_equation_2(aref, p3, m, D, t3, b):
    """
    Malconian and Modak Equation 2 for calculating Theta Parameter
    :param aref: Reference area (m^2)
    :param p3: Stagnation pressure at combustor inlet (Pa)
    :param m: mass flow rate (kg/s)
    :param D: Diameter of casing (m)
    :param t3: Stagnation temperature at combustor inlet (K)
    :param b: Inlet Temperature factor (K) [Find using equations in M&M]
    :return: Theta Parameter (kg^(3/4)m * s^(-3.5)
    """
    calculation = ( (p3**1.75) * aref * (D ** 0.75) * math.exp(t3/b))/m
    return calculation

def mm_length_calculation(dref):
    """
    Malconian and Modak Length Calculation
    :param dref: Reference diameter (m)
    :return: Combustor length (m)
    """
    primary_zone_length = 0.75 * dref
    secondary_zone_length = 0.5 * dref
    dilution_zone_length = 1.3 * dref
    calculation = primary_zone_length + secondary_zone_length + dilution_zone_length
    return calculation
