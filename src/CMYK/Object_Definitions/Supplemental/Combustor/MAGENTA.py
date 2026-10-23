import math
import numpy as np

def mm_aref_equation_1(p3, t3, dp34, qref, m):
    k = 143.5
    calculation = (k * (((m * math.sqrt(t3)) / p3) ** 2) * ((dp34 / qref) / (dp34 / p3))) ** 0.5
    return calculation

def mm_dref_equation(aref):
    calculation = math.sqrt((4 * aref) / math.pi)
    return calculation