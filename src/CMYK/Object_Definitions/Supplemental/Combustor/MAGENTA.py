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

def outer_diameter_reverse_flow(turbine_diameter, reference_area):
    """
    Calculates the outer diameter (R) of the combustor given the interior diameter of the sum turbine components (assuming perfect geometry)
    :param turbine_diameter: Diameter of the turbine components (m)
    :param reference_area: Reference area (m^2)
    :return: Outer Diameter (R) of the casing of the combustor
    """
    outer_diameter = ((reference_area / math.pi) + (turbine_diameter ** 2)) ** 0.5
    return outer_diameter

def format_values(outer_diameter, axial_length, reference_area):
    """
    Format the output values ( TEMP ) #TODO: MAKE UNIVERSAL FOR OUTPUTS
    :param outer_diameter: Outer diameter of the combustor (m)
    :param axial_length: Length of the combustor (m)
    :param reference_area: Reference Area (m^2)
    :return: String of the combined inputs.
    """
    outer_diameter = str(f'{outer_diameter:.2f}')
    axial_length = str(f'{axial_length:.2f}')
    reference_area = str(f'{reference_area:.2f}')
    bar = "----------------------------------------------------------"

    end_string = "COMBUSTOR SIZING" + bar + "\n" + "Axial Length: " + axial_length + "\n" + "Reference Area: " + reference_area + "\n" + "Outer Diameter: " + outer_diameter + "\n" + bar

    return end_string