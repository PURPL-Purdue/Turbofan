# Bellmouth Inlet Generation
# 10/15/2026

import numpy as np
import math as m
import matplotlib.pyplot as plt

# Inputs: mass flow, air density, inlet velocity
def bellmouth_inlet(m_dot, rho, V_i):

    A_e = m_dot / (rho * V_i)
    D_e = m.sqrt(4 * A_e / m.pi)

    D_i = 2.13 * D_e
    r_c = 0.08 * D_i
    r_e = D_e / 2
    r_i = D_i / 2
    l = D_e

    r_c_theta = np.linspace(m.pi/2, m.pi, 200)
    ellipse_theta = np.linspace(0, m.pi / 2, 200)
    z_ellipse = l * (1 - np.sin(ellipse_theta))
    R_ellipse_upper = r_e * (1 - np.cos(ellipse_theta)) + r_e
    z_r_c = r_c * (1 - np.sin(r_c_theta))
    R_r_c_upper = r_c * (1 - np.cos(r_c_theta)) + R_ellipse_upper[len(R_ellipse_upper) - 1] - r_c

    R_ellipse_lower = -R_ellipse_upper
    R_r_c_lower = -R_r_c_upper

    print("Mouth Diameter: ", f"{D_i:.2f}")
    print("Exit Diameter: ", f"{D_e:.2f}")
    print("Corner Radius ", f"{r_c:.2f}")

    plt.figure(figsize = (5, 5))
    plt.plot(z_r_c, R_r_c_upper, color = "blue")
    plt.plot(z_ellipse, R_ellipse_upper, color = "blue")
    plt.plot(z_r_c, R_r_c_lower, color = "blue")
    plt.plot(z_ellipse, R_ellipse_lower, color = "blue")
    plt.vlines(x = l, ymin = -r_e, ymax = r_e, color = "blue")
    plt.vlines(x = min(z_ellipse), ymin = min(R_ellipse_lower), ymax = max(R_ellipse_upper), color = "blue")
    plt.hlines(y = 0, xmin = 0, xmax = l, color = "blue", linestyles = "--")
    plt.axis("equal")
    plt.show()

bellmouth_inlet(10, 1.225, 10)