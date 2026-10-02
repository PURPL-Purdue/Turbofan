from Object_Definitions.Supplemental.Turbine.YELLOW import YELLOW

R = 75 # radius
Cx = 28 # axial chord (Setting to 0.0 triggers default based on incompressible Zweifel loading coefficient of 0.8)
Ct = 15 # tangential chord (Setting to 0.0 triggers default assuming d(beta)/dx = constant)
zeta = 6.5 # unguided turning (Setting to <= 0.0 triggers default of 0.0001)
beta_in = 45 # inlet blade angle
eps = 9.00 # inlet wedge angle
R_LE = 0.4 # leading edge radius (Values >= 2.0 are interpreted as inlet percent blockage)
beta_out = -25 # exit blade angle
R_TE = 0.8 # trailing edge radius (Values >= 2.0 are interpreted as exit percent blockage)
N_B = 30 # number of blades
o = 8.6 # throat (Setting to 0.0 triggers default blocked throat-to-pitch calculation)

YELLOW(R, Cx, Ct, zeta, beta_in, eps, R_LE, beta_out, R_TE, N_B, o)