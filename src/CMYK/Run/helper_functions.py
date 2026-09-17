import numpy as np

def T_T0(gamma: float, M: float) -> float:
    """Calculates and returns T/T0 as per the isentropic state definition"""
    return (1 + (gamma-1)/2*M**2)**-1

def P_P0(gamma: float, M: float) -> float:
    """Calculates and returns P/P0 as per the isentropic state definition"""
    return (1 + (gamma-1)/2*M**2)**(-gamma/(gamma-1))

def rho_rho0(gamma: float, M: float) -> float:
    """Calculates and returns rho/rho0 as per the isentropic state definition"""
    return (1 + (gamma-1)/2*M**2)**(-1/(gamma-1))

def M_fromTT0(gamma: float, T: float, T0: float) -> float:
    """Calculates and returns Mach number from inputting T and T0 using the isentropic definition of T/T0"""
    return np.sqrt(((T/T0)**-1 - 1)*(2/(gamma-1)))

def M_fromPP0(gamma: float, P: float, P0: float) -> float:
    """Calculates and returns Mach number from inputting P and P0 using the isentropic definition of P/P0"""
    return np.sqrt(((P/P0)**(1-gamma) - 1)*(2/(gamma-1)))

def a(gamma: float, R: float, T: float) -> float:
    """Calculates and returns the local speed of sound"""
    return np.sqrt(gamma * R * T)

def T02_T01_from_P02_P01(gamma: float, P02: float, P01: float) -> float:
    """Calculates temperature ratio from pressure ratio using isentropic relations"""
    return (P02/P01)**((gamma-1)/gamma)

def P02_P01_from_T02_T01(gamma: float, T02: float, T01: float) -> float:
    """Calculates pressure ratio from temperature ratio using isentropic relations"""
    return (T02/T01)**(gamma/(gamma-1))

def A_Astar(gamma: float, M: float) -> float:
    """Calculates and returns A/Astar as per the isentropic state definition"""
    return ((gamma+1)/2) ** (-(gamma + 1)/(2*(gamma-1))) * ((1 + (gamma-1)/2*M**2) ** ((gamma + 1)/(2*(gamma-1)))) / M

def Secant_Method(func, x0, x1, tol=1e-6, max_iter=100, args=()):
    """
    Find the root of `func` using a bracketed secant method.

    Requires func(x0) and func(x1) to have opposite signs (i.e. x0 and x1
    bracket a root). On each iteration, a secant step is attempted; if it
    would fall outside the current bracket, a bisection step is used instead.
    This guarantees the root estimate always stays inside the original
    bracket, avoiding the classic secant-method failure mode of diverging
    or converging to a spurious root outside the physically valid range.

    Parameters
    ----------
    func : callable
        Function of one variable (plus optional extra args) whose root is sought.
    x0, x1 : float
        Bracket endpoints. func(x0) and func(x1) must have opposite signs.
    tol : float
        Convergence tolerance on |f(x)|.
    max_iter : int
        Maximum number of iterations before giving up.
    args : tuple
        Extra positional arguments passed to func, i.e. func(x, *args).

    Returns
    -------
    float
        The converged root estimate.

    Raises
    ------
    ValueError
        If f(x0) and f(x1) do not have opposite signs (no bracketed root).
    RuntimeError
        If the method fails to converge within max_iter iterations.
    """
    f0 = func(x0, *args)
    f1 = func(x1, *args)

    if f0 == 0:
        return x0
    if f1 == 0:
        return x1

    if f0 * f1 > 0:
        raise ValueError(
            f"Secant_Method: f(x0) and f(x1) must have opposite signs "
            f"(no bracketed root). f(x0={x0})={f0}, f(x1={x1})={f1}"
        )

    # maintain bracket [a, b] such that f(a) and f(b) have opposite signs
    a, fa = x0, f0
    b, fb = x1, f1

    for i in range(max_iter):
        # --- attempt a secant step using the two most recent points ---
        if fa != fb:
            x_secant = b - fb * (b - a) / (fb - fa)
        else:
            x_secant = None

        # if secant step is invalid or falls outside the bracket, bisect instead
        lo, hi = (a, b) if a < b else (b, a)
        if x_secant is None or not (lo < x_secant < hi):
            x_new = 0.5 * (a + b)
        else:
            x_new = x_secant

        f_new = func(x_new, *args)

        if abs(f_new) < tol:
            return x_new

        # update bracket: keep the half that still contains a sign change
        if fa * f_new < 0:
            b, fb = x_new, f_new
        else:
            a, fa = x_new, f_new

    raise RuntimeError(
        f"Secant_Method: failed to converge after {max_iter} iterations "
        f"(last x={x_new}, f={f_new})"
    )