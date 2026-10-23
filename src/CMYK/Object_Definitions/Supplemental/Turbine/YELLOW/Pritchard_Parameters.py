# WARNING: THE FOLLOWING CODE WAS COMPLETELY WRITTEN BY AI TO TEST CHANGES TO Pritchard_Parameters_V1.py
# THIS CODE WORKS SOMEHOW
# I will come back and fix any issues but right now it just needs to work - Paul Piros

"""
Pritchard (1985) 11-parameter airfoil inputs from meanline quantities,
following the procedure in "Parameter obtention" (Aungier 2006, Ch. 4, 6, 7;
Kacker & Okapuu 1982).

Inputs : beta1, beta2 (blade angles, deg), N (blades), R (mean radius), M2 (exit Mach)
Outputs: the 11 Pritchard parameters + intermediate quantities

ANGLE CONVENTION
Aungier's equations used here (s/c optimum, ACL/TCL, O = s*sin(beta_g),
deviation) measure angles from the TANGENTIAL direction. The Kacker-Okapuu
stagger chart measures them from the AXIAL direction. The function takes
beta1, beta2 in Aungier's (tangential) convention by default and converts
internally for the stagger fit:  beta_axial = 90 - beta_tangential.
Pass angle_ref="axial" if your inputs are measured from axial.
"""
# TODO: Fix erroneous outputs

import math
import warnings

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def sind(a): return math.sin(math.radians(a))
def cosd(a): return math.cos(math.radians(a))
def asind(x): return math.degrees(math.asin(x))

def stagger_KO(b1_ax, b2_ax_mag):
    """
    Kacker & Okapuu (1982) Fig. 5 quartic fit.
    b1_ax     : inlet blade angle from axial [deg] (-30 <= b1_ax <= 70)
    b2_ax_mag : exit blade angle magnitude from axial [deg] (50 <= b2_ax_mag <= 80)
    Returns stagger angle measured from AXIAL [deg].
    """
    x, y = (b1_ax - 20.0) / 50.0, (b2_ax_mag - 65.0) / 15.0
    theta = (40.67 + 23.71*y + 5.097*y**2 - 1.498*y**3 - 1.605*y**4
             + x*(-21.79 + 13.96*y + 5.148*y**2 - 1.668*y**3)
             + x**2*(-3.241 + 0.5814*y + 0.7642*y**2)
             + x**3*(1.367 - 1.172*y)
             - 0.3178*x**4)
    return max(theta, 0.0)

def optimum_pitch_chord(b1_t, b2_t):
    """
    Ainley-Mathieson minimum-profile-loss s/c (Aungier 2006, Eq. 4.19-4.22).
    b1_t : inlet angle from tangential [deg] (90 = axial inlet, >90 = positive camber/impulse)
    b2_t : exit angle from tangential [deg] (0 < b2_t < 90, e.g. 20 deg)
    """
    sc0 = 0.427 + b2_t / 58.0 - (b2_t / 93.0) ** 2       # Nozzle (b1_t = 90)
    sc1 = 0.224 + (1.575 - b2_t / 90.0) * (b2_t / 90.0)  # Impulse (b1_t = 180 - b2_t)

    # FIXED SIGN: xi = +1 at impulse (b1_t = 180 - b2_t), xi = 0 at axial inlet (b1_t = 90)
    xi = (b1_t - 90.0) / (90.0 - b2_t)
    return sc0 + (sc1 - sc0) * abs(xi) * xi

def deviation(beta_g_t, M2):
    """Aungier (2006) Eq. 4.13-4.14 subsonic deviation. beta_g_t in deg from tangential."""
    os_ = sind(beta_g_t)                                 # o/s = sin(beta_g)
    arg = os_ * (1.0 + (1.0 - os_) * (beta_g_t / 90.0) ** 2)
    delta0 = asind(min(max(arg, -1.0), 1.0)) - beta_g_t
    if M2 <= 0.5:
        return delta0
    X = 2.0 * M2 - 1.0
    return delta0 * (1.0 - 10.0 * X**3 + 15.0 * X**4 - 6.0 * X**5)

def solve_gauging(b2_t, s, M2, tol=1e-8, max_iter=200):
    """Fixed-point iteration for tangential gauging angle beta_g_t and throat O."""
    beta_g_t = b2_t
    delta = 0.0
    for i in range(max_iter):
        new_delta = deviation(beta_g_t, M2)
        beta_g_t = b2_t - new_delta
        if abs(new_delta - delta) < tol:
            break
        delta = new_delta
    else:
        warnings.warn("Gauging-angle iteration did not converge")
    O = s * sind(beta_g_t)
    return beta_g_t, new_delta, O, i + 1

def get_pritchard_params(beta1, beta2, N, R, M2, *,
                         R_LE=None, R_TE=None, wedge_in=None, ugt=5.0,
                         angle_ref="tangential"):
    """
    If angle_ref="tangential" (matches your 64.4869 and -23.6712 inputs!):
      - beta1 is measured from tangential (e.g. 64.49 deg -> 25.51 deg from axial)
      - beta2 is measured from tangential (e.g. -23.67 deg -> -66.33 deg from axial)
    If angle_ref="axial":
      - beta1 is measured from axial (e.g. 25.51 deg)
      - beta2 is measured from axial (e.g. -66.33 deg)
    """
    if M2 > 1.0:
        raise ValueError("Procedure covers subsonic exit only (M2 <= 1).")

    if angle_ref == "tangential":
        # Convert your tangential inputs (e.g. 64.49, -23.67) to axial angles:
        b1_ax = 90.0 - beta1            # e.g. 90 - 64.4869 = +25.5131 deg (from axial)
        b2_t  = abs(beta2)              # e.g. 23.6712 deg (from tangential)
        b2_ax_mag = 90.0 - b2_t         # e.g. 66.3288 deg (from axial)
        b1_t  = 90.0 + b1_ax            # Aungier tangential (90 = axial, >90 = positive camber)
    elif angle_ref == "axial":
        b1_ax = beta1                   # e.g. +25.5131 deg (from axial)
        b2_ax_mag = abs(beta2)          # e.g. 66.3288 deg (from axial)
        b1_t  = 90.0 + b1_ax
        b2_t  = 90.0 - b2_ax_mag
    else:
        raise ValueError("angle_ref must be 'axial' or 'tangential'")

    # --- Pitch ---
    s = 2.0 * math.pi * R / N

    # --- Stagger (from axial) and Setting Angle gamma (from tangential) ---
    stagger = stagger_KO(b1_ax, b2_ax_mag)
    gamma = 90.0 - stagger

    # --- True chord from optimum s/c ---
    sc_opt = optimum_pitch_chord(b1_t, b2_t)
    c = s / sc_opt

    # --- Designer choices ---
    if R_LE is None:
        R_LE = 0.05 * c
    if R_TE is None:
        R_TE = 0.01 * c
    if wedge_in is None:
        wedge_in = 10.0

    # --- Axial and Tangential Chord (using AXIAL angles to match Pritchard LE/TE circles) ---
    ACL = c * sind(gamma) + R_LE * (1.0 - sind(b1_ax)) + R_TE * (1.0 - sind(b2_ax_mag))
    TCL = c * cosd(gamma) + R_LE * cosd(b1_ax) - R_TE * cosd(b2_ax_mag)

    # --- Throat and Gauging Angle ---
    beta_g_t, delta, O, n_iter = solve_gauging(b2_t, s, M2)

    # Return axial angles for Pritchard (beta_in > 0, beta_out < 0)
    pritchard = {
        "R (radius)":               R,
        "Cx (axial chord)":         ACL,
        "Ct (tangential chord)":    TCL,
        "unguided turning [deg]":   ugt,
        "beta_in [deg]":            b1_ax,          # +25.5131 deg
        "inlet half-wedge [deg]":   wedge_in,
        "R_LE":                     R_LE,
        "beta_out [deg]":           -b2_ax_mag,     # -66.3288 deg
        "R_TE":                     R_TE,
        "N (blades)":               N,
        "O (throat)":               O,
    }

    extra = {
        "pitch s":                  s,
        "(s/c)_opt":                sc_opt,
        "chord c":                  c,
        "stagger (from axial)":     stagger,
        "setting angle gamma":      gamma,
        "gauging angle beta_g_t":   beta_g_t,
        "deviation delta":          delta,
        "o/s":                      O / s,
        "iterations":               n_iter,
    }
    return pritchard, extra