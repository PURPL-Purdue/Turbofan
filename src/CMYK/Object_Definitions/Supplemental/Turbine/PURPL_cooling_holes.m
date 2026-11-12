% PURPL Cooling Hole Code

% Parameters
A_shiled = ;
p3 = 10;         % inlet combustions pressure (bar)
C_dd = ;       % Discharge Coefficient
rho3 = ;       % inlet combustion density
Delta_P_liner = ; %pressure difference at the liner wall 
d_hole = ; % diameter of cooling holes
p_atm = 101325; % atmospheric pressure (Pa)

%code

mdot_a_dome = 0.5 * A_shiled * (p3/p_atm);

A_dome = mdot_a_dome/(C_dd*sqrt(2*rho3*Delta_P_liner));

N_dome_hole = 4*A_dome/(pi * d_hole^2);


