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

import math
import warnings

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def sind(a): return math.sin(math.radians(a))
def cosd(a): return math.cos(math.radians(a))
def asind(x): return math.degrees(math.asin(x))


def stagger_KO(b1, b2):
    """Kacker & Okapuu (1982) Fig. 5, quartic fit. Degrees, measured from axial;
    valid -30<=b1<=70, 50<=b2<=80."""
    x, y = (b1 - 20) / 50, (b2 - 65) / 15
    theta = (40.67 + 23.71*y + 5.097*y**2 - 1.498*y**3 - 1.605*y**4
             + x*(-21.79 + 13.96*y + 5.148*y**2 - 1.668*y**3)
             + x**2*(-3.241 + 0.5814*y + 0.7642*y**2)
             + x**3*(1.367 - 1.172*y)
             - 0.3178*x**4)
    return max(theta, 0.0)


def optimum_pitch_chord(beta1, beta2):
    """Ainley-Mathieson minimum-profile-loss s/c (Aungier fit).
    beta1, beta2 in deg from tangential."""
    sc0 = 0.427 + beta2 / 58 - (beta2 / 93) ** 2           # nozzle (axial inlet)
    sc1 = 0.224 + (1.575 - beta2 / 90) * (beta2 / 90)       # impulse
    xi = (90 - beta1) / (90 - beta2)
    return sc0 + (sc1 - sc0) * abs(xi) * xi


def deviation(beta_g, M2):
    """Aungier subsonic deviation. beta_g in deg from tangential."""
    os_ = sind(beta_g)                                       # o/s = sin(beta_g)
    arg = os_ * (1 + (1 - os_) * (beta_g / 90) ** 2)
    delta0 = asind(min(arg, 1.0)) - beta_g
    if M2 <= 0.5:
        return delta0
    X = 2 * M2 - 1
    return delta0 * (1 - 10 * X**3 + 15 * X**4 - 6 * X**5)


def solve_gauging(beta2, s, M2, tol=1e-8, max_iter=200):
    """Fixed-point iteration, steps 1-7 of the procedure."""
    beta_g = beta2                                # step 1: zero deviation
    delta = 0.0
    for i in range(max_iter):
        new_delta = deviation(beta_g, M2)         # steps 2-3
        beta_g = beta2 - new_delta                # step 4
        if abs(new_delta - delta) < tol:          # step 6
            break
        delta = new_delta
    else:
        warnings.warn("Gauging-angle iteration did not converge")
    O = s * sind(beta_g)                          # steps 5 / 7
    return beta_g, new_delta, O, i + 1


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------
def pritchard_params(beta1, beta2, N, R, M2, *,
                     R_LE=None, R_TE=None, wedge_in=None, ugt=None,
                     angle_ref="tangential"):
    """
    beta1, beta2 : inlet / exit blade angles [deg]
    N            : number of blades
    R            : mean radius [any length unit; all lengths come out in it]
    M2           : exit Mach number (subsonic only, M2 <= 1)

    Designer choices (Aungier 7.4). If left as None, PLACEHOLDER values are
    used (NOT from Aungier -- replace with your own choices):
        R_LE     : leading-edge radius       (placeholder 0.05*c)
        R_TE     : trailing-edge radius      (placeholder 0.01*c)
        wedge_in : inlet half-wedge angle, deg (placeholder 10 deg)
        ugt      : unguided turning, deg -- not yet in the procedure,
                   returned as None unless supplied
    """
    if M2 > 1:
        raise ValueError("Procedure covers subsonic exit only (M2 <= 1).")

    # --- convert to both conventions ---
    if angle_ref == "tangential":
        b1_t, b2_t = beta1, beta2
    elif angle_ref == "axial":
        b1_t, b2_t = 90 - beta1, 90 - beta2
    else:
        raise ValueError("angle_ref must be 'tangential' or 'axial'")
    b1_ax, b2_ax = 90 - b1_t, 90 - b2_t

    # --- pitch ---
    s = 2 * math.pi * R / N

    # --- stagger (axial) and setting angle (tangential) ---
    if not (-30 <= b1_ax <= 70 and 50 <= b2_ax <= 80):
        warnings.warn(f"Angles (axial ref) b1={b1_ax:.1f}, b2={b2_ax:.1f} "
                      "outside K-O fit range (-30..70, 50..80); stagger extrapolated")
    stagger = stagger_KO(b1_ax, b2_ax)
    gamma = 90 - stagger

    # --- chord from optimum s/c ---
    sc_opt = optimum_pitch_chord(b1_t, b2_t)
    c = s / sc_opt

    # --- designer choices ---
    placeholders = []
    if R_LE is None:
        R_LE = 0.05 * c; placeholders.append("R_LE")
    if R_TE is None:
        R_TE = 0.01 * c; placeholders.append("R_TE")
    if wedge_in is None:
        wedge_in = 10.0; placeholders.append("wedge_in")
    if placeholders:
        warnings.warn("Placeholder values used for: " + ", ".join(placeholders))

    # --- axial and tangential chord (Aungier Ch. 7) ---
    ACL = c * sind(gamma) + R_LE * (1 - sind(b1_t)) + R_TE * (1 - sind(b2_t))
    TCL = c * cosd(gamma) + R_LE * cosd(b1_t) - R_TE * cosd(b2_t)

    # --- throat and gauging angle ---
    beta_g, delta, O, n_iter = solve_gauging(b2_t, s, M2)

    pritchard = {
        "R (radius)":               R,
        "Cx (axial chord)":         ACL,
        "Ct (tangential chord)":    TCL,
        "beta_in [deg]":            beta1,
        "inlet half-wedge [deg]":   wedge_in,
        "R_LE":                     R_LE,
        "beta_out [deg]":           beta2,
        "R_TE":                     R_TE,
        "N (blades)":               N,
        "O (throat)":               O,
        "unguided turning [deg]":   ugt,
    }
    extra = {
        "pitch s":                  s,
        "(s/c)_opt":                sc_opt,
        "chord c":                  c,
        "stagger (from axial)":     stagger,
        "setting angle gamma":      gamma,
        "gauging angle beta_g":     beta_g,
        "deviation delta":          delta,
        "o/s":                      O / s,
        "iterations":               n_iter,
        "angle convention":         angle_ref,
        "placeholders used":        placeholders,
    }
    return pritchard, extra


def print_results(pritchard, extra):
    print("Pritchard 11 parameters")
    for k, v in pritchard.items():
        print(f"  {k:26s} {v if v is None or isinstance(v, int) else round(v, 5)}")
    print("Intermediate values")
    for k, v in extra.items():
        print(f"  {k:26s} {round(v, 5) if isinstance(v, float) else v}")


if __name__ == "__main__":
    # Example stator: axial inlet (90 deg from tangential), exit 20 deg from
    # tangential (70 deg from axial), 30 blades, R = 0.05 m, M2 = 0.7
    p, e = pritchard_params(beta1=45, beta2=-25, N=30, R=75, M2=0.7)
    print_results(p, e)