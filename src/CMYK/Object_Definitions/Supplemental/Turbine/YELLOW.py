from dataclasses import dataclass
from scipy.optimize import minimize_scalar
import numpy as np

from ..Curve import *

# TODO: check if faulty logic is present or inputs in YELLOW_TEST.py are bad

def YELLOW(R, Cx, Ct, zeta, beta_in, eps, R_LE, beta_out, R_TE, N_B, o):
    params = getPritchardParams(R, Cx, Ct, zeta, beta_in, eps, R_LE, beta_out, R_TE, N_B, o, 0.5 * zeta)
    #params.eps_out = optimize_exit_half_wedge_angle(params)
    print(params.eps_out, 0.5 * params.zeta)
    Points = getPritchardPoints(params)
    X,Y = BuildBlade(Points)


def getPritchardParams(R, Cx, Ct, zeta, beta_in, eps, R_LE, beta_out, R_TE, N_B, o, eps_out):

    return PritchardParams(
        R, Cx, Ct, zeta, beta_in, eps,
        R_LE, beta_out, R_TE, N_B, o, eps_out
    )

def getPritchardPoints(params):
    P1 = ReferencePoint(*get_point_1(params))
    P2 = ReferencePoint(*get_point_2(params))
    P3 = ReferencePoint(*get_point_3(params))
    P4 = ReferencePoint(*get_point_4(params))
    P5 = ReferencePoint(*get_point_5(params))

    return P1, P2, P3, P4, P5

def BuildBlade(Points):
    P1 = Points[0]
    P2 = Points[1]
    P3 = Points[2]
    P4 = Points[3]
    P5 = Points[4]
    
    X,Y = build_blade(P1, P2, P3, P4, P5)

    return X, Y


def get_point_1(params):
    beta_1 = params.beta_out - params.eps_out
    # convert degree to radians for trig functions to work
    beta_1_rad = np.radians(beta_1)

    x1 = params.Cx - params.R_TE * (1 + np.sin(beta_1_rad))
    y1 = params.R_TE * (np.cos(beta_1_rad))
    m1 = np.tan(beta_1_rad)

    return x1, y1, m1

def get_point_2(params):
    beta_2 = params.beta_out - params.eps_out + params.zeta
    # convert degree to radians for trig functions to work
    beta_2_rad = np.radians(beta_2)

    x2 = params.Cx - params.R_TE + (params.o + params.R_TE) * np.sin(beta_2_rad)
    y2 = (2 * np.pi * params.R / params.N_B) - (params.o + params.R_TE) * np.cos(beta_2_rad)
    m2 = np.tan(beta_2_rad)

    return x2, y2, m2

def get_point_3(params):
    beta_3 = params.beta_in + 0.5 * params.eps
    # convert degree to radians for trig functions to work
    beta_3_rad = np.radians(beta_3)

    x3 = params.R_LE * (1 - np.sin(beta_3_rad))
    y3 = params.Ct + params.R_LE * np.cos(beta_3_rad)
    m3 = np.tan(beta_3_rad)

    return x3, y3, m3

def get_point_4(params):
    beta_4 = params.beta_in - (0.5 * params.eps)
    # convert degree to radians for trig functions to work
    beta_4_rad = np.radians(beta_4)

    x4 = params.R_LE * (1 + np.sin(beta_4_rad))
    y4 = params.Ct - (params.R_LE * np.cos(beta_4_rad))
    m4 = np.tan(beta_4_rad)

    return x4, y4, m4

def get_point_5(params):
    beta_5 = params.beta_out + params.eps_out
    # convert degree to radians for trig functions to work
    beta_5_rad = np.radians(beta_5)

    x5 = params.Cx - params.R_TE * (1 - np.sin(beta_5_rad))
    y5 = -1 * params.R_TE * np.cos(beta_5_rad)
    m5 = np.tan(beta_5_rad)

    return x5, y5, m5

def optimize_exit_half_wedge_angle(params):
    """

    :param params:
    :return:
    """
    # initial condition for exit half wedge angle
    # given by ...
    result = minimize_scalar(lambda eps_out: get_throat_y_error(params.R,
                                                                params.Cx,
                                                                params.Ct,
                                                                params.zeta,
                                                                params.beta_in,
                                                                params.eps,
                                                                params.R_LE,
                                                                params.beta_out,
                                                                params.R_TE,
                                                                params.N_B,
                                                                params.o,
                                                                eps_out))

    eps_out = result.x
    print(result.fun)
    return eps_out

def get_throat_y_error(R, Cx, Ct, zeta, beta_in, eps, R_LE, beta_out, R_TE, N_B, o, eps_out):
    """

    :param params:
    :return:
    """
    params = getPritchardParams(R, Cx, Ct, zeta, beta_in, eps, R_LE, beta_out, R_TE, N_B, o, eps_out)
    P_1 = ReferencePoint(*get_point_1(params))
    P_2 = ReferencePoint(*get_point_2(params))
    P_3 = ReferencePoint(*get_point_3(params))

    C12 = Curve(P_1, P_2)
    C23 = Curve(P_2, P_3)

    C12.build_circularArc()
    C23.build_quadraticBezier()

    x12, y12 = points_to_arrays(C12.curve)
    x23, y23 = points_to_arrays(C23.curve)

    throat_y_error = abs(y23[0] - y12[-1])

    return throat_y_error

@dataclass
class PritchardParams:
    R: float # radius
    Cx: float # axial chord
    Ct: float # tangential chord
    zeta: float # unguided turning
    beta_in: float # inlet blade angle
    eps: float # inlet wedge angle
    R_LE: float # leading edge radius
    beta_out: float # exit blade angle
    R_TE: float # trailing edge radius
    N_B: int # number of blades
    o: float # throat
    eps_out: float # ADD COMMENTS