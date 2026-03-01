clear;clc;clf

load("Turbofan.mat")

%% Design Variables
% Constants
gamma = 1.4;     %1.4;    % Specific heat ratio           |
cp = 1004.5000000000001;              %1004;      % Specific heat                 | J/(kg*K)


% Inlet Conditions
T0_1m = 348.38679918684875; %298;      % Inlet total temperature     | Kelvin        (absolute) spanwise constant
P0_1m = 162080.0; %101000;   % Inlet total pressure        | Pascals       (absolute) spanwise constant


% Design choices
Pr_total = 12; %20;  % Overall pressure ratio        |
e_c = 0.9;      % Polytropic efficiency         |
% m_dot = Turbofan.Specs.Info.core_mass_flow_air; %100;    % Mass flow rate                | kg/s
htt_rr = 0.6;   % Hub to tip radius ratio       |
deHaller = 0.72;            % typical value
min_reynolds = 300000;
kin_visc = 1.46e-5;                           % | From chart, 0km

alpha_1m = 30;                                 % | Inlet Swirl, degrees
Mz_1m = 0.45;                                  % | Initial axial mach number
U_tip_1 = 350;                                  % | Inlet rotor tip speed, m/s

r_tip_1 = 100 / 1000;                           % | Inlet tip radius, mm / 1000 to get meters

%% Compressor inlet conditions
% Design assumptions
Mc_1m = Mz_1m/cosd(alpha_1m);

% Station 1 Static Pressure and Temperature
T_1m = T0_1m/(1+(gamma-1)*Mc_1m^2/2);
P_1m = P0_1m/(1+(gamma-1)*Mc_1m^2/2)^(gamma/(gamma-1));

R = (gamma-1)*cp/gamma;
rho_1m = P_1m/(R*T_1m);
a_1m = sqrt((gamma-1)*cp*T_1m);
z_1m = Mz_1m*a_1m;
C_1m = Mc_1m*a_1m;

% Initial inlet annulus geometry, assume constant spanwise distributions
% A_1 = m_dot/rho_1/z_1m;
% r_tip_1 = sqrt(A_1/pi/(1-htt_rr^2));
r_hub_1 = r_tip_1*htt_rr;
A_1 = (r_tip_1^2 - r_hub_1^2)*pi;
m_dot = rho_1m*z_1m*A_1;

%% Compressor exit conditions
Tr_total = Pr_total^((gamma-1)/(e_c*gamma));

P0_exit_m = P0_1m * Pr_total;  % at midspan
T0_exit_m = T0_1m * Tr_total;  % at midspan

alpha_exit_m = alpha_1m;   % repeating stage | at midspan
z_exit_m = z_1m;          % design choice   | at midspan
C_exit_m = C_1m;

T_exit_m = T0_exit_m - C_exit_m^2/(2*cp); % | at midspan

a_exit_m = sqrt((gamma-1)*cp*T_exit_m);
Mz_exit_m = z_exit_m/a_exit_m;
Mc_exit_m = Mz_exit_m/cosd(alpha_exit_m);

P_exit_m = P0_exit_m/(1+(gamma-1)*Mc_exit_m^2/2)^(gamma/(gamma-1)); % | at midspan
rho_exit_m = P_exit_m/(R*T_exit_m);

% Exit annulus geometry
A_exit = m_dot/rho_exit_m/z_exit_m;

syms h
r_mean_1 = (r_tip_1 + r_hub_1)/2;
h = double(solve((r_mean_1+h)^2 - (r_mean_1-h)^2 == A_exit/pi, h));

r_hub_exit = r_mean_1 - h;
r_tip_exit = r_mean_1 + h;
% r_tip_exit = r_tip_1;
% r_hub_exit = sqrt(r_tip_exit^2 - A_exit/pi);

%% Pitchline calculations
% Design choices
solidity_rotor = 1;
solidity_stator = 1.25;

ang_vel = U_tip_1/r_tip_1;
rpm = ang_vel * 30 / pi;

% Station 1 stuff
U_1m = U_tip_1 * (r_mean_1/r_tip_1);
beta_1m = atand((U_1m-z_1m*tand(alpha_1m))/z_1m);
W_1m = z_1m / cosd(beta_1m);
Ctheta_1m = z_1m*tand(alpha_1m);
Wtheta_1m = U_1m - Ctheta_1m;

Mw_1m = W_1m/a_1m;

% Station 2 stuff
U_2m = U_1m;        % Initial Approximation, true if we adjust both hub and shroud
z_2m = z_1m;        % Design chioce

W_2m = W_1m*deHaller;      % De Haller
beta_2m = acosd(z_2m/W_2m);
Wtheta_2m = z_2m*tand(beta_2m);
Ctheta_2m = U_2m-Wtheta_2m;
C_2m = sqrt(z_2m^2 + Ctheta_2m^2);
alpha_2m = atand(Ctheta_2m/z_2m);

phi_2m = z_2m/U_2m;
psi_2m = 1 + phi_2m*(tand(-beta_2m)-tand(alpha_1m));

% Station 3 stuff
C_3m = C_1m;
W_3m = W_1m;
U_3m = U_1m;
z_3m = z_1m;
Ctheta_3m = Ctheta_1m;
Wtheta_3m = Wtheta_1m;
alpha_3m = alpha_1m;
beta_3m = beta_1m;

% Stage metrics
degR_m = 1 - (Ctheta_1m + Ctheta_2m) / (2*U_1m);
D_mr = D_factor(W_1m, W_2m, Ctheta_1m, Ctheta_2m, solidity_rotor);
D_ms = D_factor(C_2m, C_3m, Ctheta_2m, Ctheta_3m, solidity_stator);

% Stage organization
rps = struct( ...
    "C_1m", C_1m, ...
    "C_2m", C_2m, ...
    "C_3m", C_3m, ...
    "W_1m", W_1m, ...
    "W_2m", W_2m, ...
    "W_3m", W_3m, ...
    "U_1m", U_1m, ...
    "U_2m", U_2m, ...
    "U_3m", U_3m, ...
    "z_1m", z_1m, ...
    "z_2m", z_2m, ...
    "z_3m", z_3m, ...
    ...
    "Ctheta_1m", Ctheta_1m, ...
    "Ctheta_2m", Ctheta_2m, ...
    "Ctheta_3m", Ctheta_3m, ...
    "Wtheta_1m", Wtheta_1m, ...
    "Wtheta_2m", Wtheta_2m, ...
    "Wtheta_3m", Wtheta_3m, ...
    ...
    "alpha_1m", alpha_1m, ...
    "alpha_2m", alpha_2m, ...
    "alpha_3m", alpha_3m, ...
    "beta_1m", beta_1m, ...
    "beta_2m", beta_2m, ...
    "beta_3m", beta_3m, ...
    ...
    "degR_m", degR_m, ...
    "D_mr", D_mr, ...
    "D_ms", D_ms, ...
    ...
    "phi", phi_2m, ...
    "psi", psi_2m ...
    );

save("rps", "rps")

%% Staging
T0_2m = T0_1m + U_1m*(Ctheta_2m-Ctheta_1m)/cp;
T_2m  = T0_2m - C_2m^2/(2*cp);
a_2 = sqrt((gamma-1)*cp*T_2m);

Mc_2m = C_2m/a_2;

temp_rise_total = T0_exit_m - T0_1m;
temp_rise_per_stage = T0_2m - T0_1m;
num_stages_actual = temp_rise_total/temp_rise_per_stage;
num_stages = ceil(num_stages_actual);
num_stations = num_stages*2 + 1;

% stages = framework(num_stages);
% stations = framework(num_stations);
%% Per Stage State
r_hub_vec = ones(1, num_stages+1);
r_tip_vec = ones(1, num_stages+1);
rho_m_vec = ones(1, num_stages+1);
Tr_stages = ones(1, num_stages);
Pr_stages = ones(1, num_stages);
T0_stages = ones(1, num_stages+1);
P0_stages = ones(1, num_stages+1);
T0_stages(1) = T0_1m;
P0_stages(1) = P0_1m;

r_hub_vec(1) = r_hub_1;
r_tip_vec(1) = r_tip_1;

T0_current = T0_1m;
for i = 1:num_stages
    T0_next = T0_current + temp_rise_per_stage;
    Tr_stages(i) = T0_next / T0_current;
    Pr_stages(i) = Tr_stages(i)^(gamma*e_c/(gamma-1));
    T0_stages(i+1) = T0_next;
    P0_stages(i+1) = P0_stages(i)*Pr_stages(i);
    T0_current = T0_next;
end

for i = 1:num_stages+1
    [r_hub_vec(i), r_tip_vec(i), rho_m_vec(i)] = annulus_adjust(T0_stages(i), P0_stages(i), R, cp, gamma, m_dot, rps.C_3m, rps.z_3m, r_mean_1);
end



%% Compressor Thermodynamics Total Metrics
Pr_total_actual = prod(Pr_stages);
Tr_total_actual = T0_stages(end)/T0_stages(1);
P0_rise_total = P0_stages(end) - P0_stages(1);

%% Blade Design
% Supersonic rotor design
ttc_m = 0.065;
min_chord_m = min_reynolds*kin_visc/W_1m;       % meters, minimum chord to get reynolds
chord_m = 1.0*min_chord_m;

i = rad2deg(ttc_m);

dev_ang_m = abs(beta_2m-beta_1m) / 4 * sqrt(solidity_rotor) + 2;

% Camber angle
K_1m = beta_1m - i;
K_2m = beta_2m - dev_ang_m;
camber_m = K_1m - K_2m;

stagger_ang = beta_1m - camber_m/2 - i;

num_blades_rotor = 2 * pi * r_mean_1 / chord_m;

% Subsonic stator design
T0_2m = T0_1m + U_1m*(Ctheta_2m-Ctheta_1m)/cp;
T_2m  = T0_2m - C_2m^2/(2*cp);
a_2 = sqrt((gamma-1)*cp*T_2m);

Mc_2m = C_2m/a_2;

FF = Compressor_Free_Vortex(rps, r_hub_vec, r_tip_vec, ang_vel, degR_m, rho_m_vec, cp, R, T0_stages, m_dot, e_c, gamma);





%% Plotting
% Pressure Ratios (per stage)
figure(1);clf;
tiledlayout(1,4, TileSpacing='tight', Padding='tight')
nexttile
hold on
title("Pressure Ratios (per stage)")
plot(Pr_stages, '.-b')
grid minor
xlabel("stage")
ylabel("pressure ratio")

% Stage Velocity Triangles (Repeated Stages)
% figure(2);clf;
nexttile
hold on
title("Stage Velocity Triangles (Repeated Stages)")
C_1m_vec = [z_1m, Ctheta_1m];
W_1m_vec = [z_1m, -Wtheta_1m];
U_1m_vec = [0   , U_1m];
C_2m_vec = [z_2m, Ctheta_2m];
W_2m_vec = [z_2m, -Wtheta_2m];
U_2m_vec = [0   , U_2m];
plot_vel_triangle([0,0], C_1m_vec, W_1m_vec, U_1m_vec, '-b', '-r', '-k', 1)
plot_vel_triangle([1.2*z_1m,0], C_2m_vec, W_2m_vec, U_2m_vec, '-b', '-r', '-k', 1)
plot_vel_triangle([2*1.2*z_1m,0], C_1m_vec, W_1m_vec, U_1m_vec, '-b', '-r', '-k', 1)
grid minor
xlabel("z (m/s)")
ylabel("theta (m/s)")

% Temperature and Pressure at Various Stages
% figure(3);clf;
nexttile
x_axis = 1:1:num_stages+1;
title("Temperature and Pressure at Various Stages")
yyaxis left
plot(x_axis, P0_stages, '.-m')
ylabel("Total Pressure")
yyaxis right
plot(x_axis, T0_stages, '.-r')
ylabel("Total Temperature")
xlabel("Station Number")
grid minor

% Annulus geometry
% figure(4);clf;
nexttile
hold on
title("Annulus geometry")
x_axis = 1:1:num_stages+1;
x_axis = (x_axis-1) * 2 * chord_m;
plot(x_axis, [r_hub_vec', r_tip_vec'], '.-r')
plot(x_axis, [-r_hub_vec', -r_tip_vec'], '.-r')
x_axis_long = 1:1:FF.num_stations;
x_axis_long = (x_axis_long-1) * chord_m;
plot(x_axis_long, [FF.r_hub_vec_full', FF.r_tip_vec_full'], '.-k')
plot(x_axis_long, [-FF.r_hub_vec_full', -FF.r_tip_vec_full'], '.-k')
% ylim([0,max(r_tip_vec)*1.2])
ylim([-max(r_tip_vec)*1.2,max(r_tip_vec)*1.2])
xlim([x_axis(1), x_axis(end)])
pbaspect([range(x_axis),2*max(r_tip_vec)*1.2,1])
grid minor
xlabel("z (m)")
ylabel("r (m)")

plot_spanwise_distributions(num_stages, num_stations, chord_m, r_mean_1, r_hub_vec, r_tip_vec, FF)

%% Info dump
fprintf("======== Compressor Information ========\n")
fprintf("Ratios:\n")
fprintf("    Total Pressure Ratio (design):    %12.3f\n",       Pr_total)
fprintf("    Total Pressure Ratio (actual):    %12.3f\n",       Pr_total_actual)
fprintf("    Total Temperature Ratio (design): %12.3f\n",       Tr_total)
fprintf("    Total Temperature Ratio (actual): %12.3f\n",       Tr_total_actual)
fprintf("Values:\n")
fprintf("    Temperature Rise (total):         %12.3f K\n",     temp_rise_total)
fprintf("    Temperature Rise (per stage):     %12.3f K\n",     temp_rise_per_stage)
fprintf("    Pressure Rise (total):            %12.3f Pa\n",    P0_rise_total)
fprintf("    Inlet Total Temperature (total):  %12.3f K\n",     T0_stages(1))
fprintf("    Inlet Total Pressure (total):     %12.3f Pa\n",    P0_stages(1))
fprintf("    Exit Total Temperature (total):   %12.3f K\n",     T0_stages(end))
fprintf("    Exit Total Pressure (total):      %12.3f Pa\n",    P0_stages(end))
fprintf("Aerodynamics:\n")
fprintf("    Rotor Diffusion Factor:           %12.3f\n",       rps.D_mr)
fprintf("    Stator Diffusion Factor:          %12.3f\n",       rps.D_ms)
fprintf("    Stage Degree of Reaction:         %12.3f\n",       rps.degR_m)
fprintf("    De Haller Ratio Used:             %12.3f\n",       deHaller)
fprintf("    Rotor Inlet Mach Number:          %12.3f\n",       Mw_1m)
fprintf("    Stator Inlet Mach Number:         %12.3f\n",       Mc_2m)
fprintf("    Compressor Inlet Mach Number:     %12.3f\n",       Mc_1m)
fprintf("    Compressor Outlet Mach Number:    %12.3f\n",       Mc_exit_m)
fprintf("Triangles:\n")
fprintf("    Rotor Turning:                    %12.3f deg\n",   abs(beta_2m - beta_1m))
fprintf("    Stator Turning:                   %12.3f deg\n",   abs(alpha_1m - alpha_2m))
fprintf("Misc:\n")
fprintf("    Number of Stages (calculated):    %12.3f\n",       num_stages_actual)
fprintf("    Number of Stages (rounded up):    %12.3f\n",       num_stages)
fprintf("    Blade Chord Length:               %12.3f m\n",     chord_m)
fprintf("    RPM:                              %12.3f rpm\n",   rpm)
fprintf("    Mass Flow:                        %12.3f kg/s\n",  m_dot)
fprintf("    Inlet Tip Diameter:               %12.3f mm\n",  FF.r_tip_vec_full(1)*2*1000)
fprintf("\n======== Warnings ========\n")

%% Functions
function D = D_factor(W1, W2, Ctheta_1, Ctheta_2, sigma)
    % Diffusion factor, generally should be greater than 0.55 to prevent boundary layer separation
    D = 1- W2/W1 + abs(Ctheta_1 - Ctheta_2)/(2*sigma*W1);
end

function plot_vel_triangle(origin, C, W, U, C_style, W_style, U_style, scale)
    C = C.*scale;
    W = W.*scale;
    U = U.*scale;
    quiver(origin(1), origin(2), C(1), C(2), 0, C_style)
    quiver(origin(1), origin(2), W(1), W(2), 0, W_style)
    quiver(origin(1)+W(1), origin(2)+W(2), U(1), U(2), 0, U_style)
end

function [r_hub, r_tip, rho_m] = annulus_adjust(T0, P0, R, cp, gamma, m_dot, C, z, r_mean)    
    T = T0 - C^2/(2*cp); % | spanwise constant (design choice i think)
    
    a = sqrt((gamma-1)*cp*T);
    Mc = C/a;
    
    P = P0/(1+(gamma-1)*Mc^2/2)^(gamma/(gamma-1)); % | spanwise constant (design choice i think)
    rho_m = P/(R*T);

    A = m_dot/rho_m/z;

    syms h
    h = double(solve((r_mean+h)^2 - (r_mean-h)^2 == A/pi, h));

    r_hub = r_mean - h;
    r_tip = r_mean + h;
end