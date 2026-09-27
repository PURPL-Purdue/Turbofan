import math
import numpy as np
from matplotlib import pyplot as plt
"""
Creates quadratic bezier curves and circular arcs to construct 
Turbine Geometry given 5 points and slopes from Pritchard Method.

See PritchardTest.py for usage example

Author: Dev Patel
"""

class Curve(object):
    def __init__(self, P_0, P_2):
        self.P_0 = P_0
        self.P_2 = P_2

        self.endpoints = [self.P_0, self.P_2]
        self.curve = []

    def build_quadraticBezier(self):
        P_0 = self.P_0
        P_2 = self.P_2
        P_1 = point_center(P_0, P_2)

        self.endpoints = [P_0, P_1, P_2]
        self.curve = get_quadraticBezier(P_0, P_1, P_2)

        return self.curve


    def build_circularArc(self):
        P_0 = self.P_0
        P_2 = self.P_2

        self.endpoints = [P_0, P_2]
        self.curve = get_circularArc(P_0, P_2)




class Point(object):
    """docstring for Point"""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def product(self, constant):
        return Point(self.x*constant, self.y*constant)

    def sum(self, point):
        return Point(self.x + point.x, self.y + point.y)

    def __str__(self):
        return f"x: {self.x}, y: {self.y} \n"

class ReferencePoint(Point):
    """docstring for ReferencePoint"""
    def __init__(self, x, y, m):
        super().__init__(x, y)
        self.m = m

    def __str__(self):
        return f"x: {self.x}, y: {self.y}, m: {self.m}\n"

def point_center(P0, P1):
    x0 = P0.x
    y0 = P0.y
    x1 = P1.x
    y1 = P1.y
    m0 = P0.m
    m1 = P1.m

    xc = ((y0-y1) - m0*x0 + m1*x1)/(m1-m0)
    yc = y0 + m0*(xc-x0)

    return ReferencePoint(xc, yc, None)

def get_quadraticBezier(P_0, P_1, P_2):
    t = np.linspace(0, 1, 1000)
    B = []

    for i in range(0, len(t)):
        c = t[i] ** 2
        b = 2 * t[i] * (1 - t[i])
        a = (1 - t[i])**2

        B.append(P_0.product(a).sum(P_1.product(b).sum(P_2.product(c))))

    return B

def get_circularArc(P_0, P_2):
    P_c = get_centerpoint(P_0, P_2)
    R_c = get_arcRadius(P_0, P_c)
    (a1, a2) = get_theta_bounds(P_0, P_c, P_2)

    if(a2<a1):
        a2 += 2 * math.pi

    t = np.linspace(a1, a2, 1000)
    B = []
    for i in range(0, len(t)):
        B.append(Point(R_c * math.cos(t[i]) + P_c.x, R_c * math.sin(t[i]) + P_c.y))

    return B

def get_centerpoint(P_0, P_1):
    y1 = P_0.y
    y2 = P_1.y
    x1 = P_0.x
    x2 = P_1.x
    m1 = P_0.m
    m2 = P_1.m

    xc = (y1- y2 + x1/m1 - x2/m2) / (1/m1 - 1/m2)
    yc = y1 - (xc-x1)/m1

    return Point(xc, yc)

def get_arcRadius(P_1, P_c):
    xc = P_c.x
    yc = P_c.y
    x1 = P_1.x
    y1 = P_1.y

    Rc = math.sqrt((x1-xc)**2 + (y1-yc)**2)

    return Rc

def get_theta_bounds(P_0, P_c, P_2):
    y2 = P_2.y
    x2 = P_2.x
    y1 = P_0.y
    x1 = P_0.x
    yc = P_c.y
    xc = P_c.x

    a2 = math.atan2((y2-yc) , (x2-xc))
    a1 = math.atan2((y1 - yc) , (x1 - xc))

    return a1, a2

def points_to_arrays(points):
    x = []
    y = []
    for k, point in enumerate(points):
        x.append(point.x)
        y.append(point.y)

    x = np.array(x)
    y = np.array(y)
    return x,y

def BuildBlade(P_1, P_2, P_3, P_4, P_5):
    C12 = Curve(P_1, P_2)
    C23 = Curve(P_2, P_3)
    C34 = Curve(P_3, P_4)
    C45 = Curve(P_4, P_5)
    C51 = Curve(P_5, P_1)

    C12.build_circularArc()
    C23.build_quadraticBezier()
    C34.build_circularArc()
    C45.build_quadraticBezier()
    C51.build_circularArc()

    x12, y12 = points_to_arrays(C12.curve)
    x23, y23 = points_to_arrays(C23.curve)
    x34, y34 = points_to_arrays(C34.curve)
    x45, y45 = points_to_arrays(C45.curve)
    x51, y51 = points_to_arrays(C51.curve)

    X = np.concatenate((x12, x23, x34, x45, x51))
    Y = np.concatenate((y12, y23, y34, y45, y51))

    plt.plot(X, Y)
    # plt.plot(x12, y12)
    # plt.plot(x23, y23)
    # plt.plot(x34, y34)
    # plt.plot(x45, y45)
    # plt.plot(x51, y51)
    plt.axis('equal')
    plt.show()

    return X,Y