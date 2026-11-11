%% Axial Compressor Sizing (Merged)
% By PURPL Turbojet/Turbofan Compressor Team
% Referencing Compressor Sizing & Cycle Analysis by Marvel
% Merge of: original Turbofan compressor script + HPCA_sizing_complement
%   - Inputs / inlet definition / tip-radius sizing come from the complement
%   - Meanline, staging, blade design, annulus and plotting from the original
clear;clc;clf

% load("Turbofan.mat")   % Not used by active code (only referenced in a commented-out line)

%% Constant Properties
g = 9.81; % Gravity acceleration [m/s^2]

%% Parameter definitions (From Cycle Analysis & Sizing)
cp = 1007;                     % Specific heat [J/(kg*K)]
gamma = 1.402;                 % Specific heat ratio [Unitless]
N = 36000;                     % HP spool shaft speed [rpm] (used when fix_speed = "rpm")
alpha_1m = 30;                 % Inlet absolute flow angle [degrees]
httrr = 0.6;                   % Hub to tip radius ratio (minimum 0.55 per Farokhi)
fix_speed = "rpm";             % "rpm"     : N is fixed, tip Mach number is an output
                               % "tipmach" : Mu_1t_max is fixed, N is an output
bypass = 4;                    % Bypass ratio
mdot = 22.520;                 % Total mass flow rate [kg/s]
mdot_core = mdot/(1+bypass);   % Core mass flow rate [kg/s]
Mz_1m = 0.5;                   % Inlet axial Mach number [Unitless]
Mu_1t_max = 0.95;              % Inlet tip tangential Mach number (limit, or setpoint if fix_speed = "tipmach")

% HPCA Inlet / Fan Exit (Station 1)
P0_1m = 141820;                % Inlet meanline total pressure [Pa]
T0_1m = 336.032;               % Inlet meanline total temperature [K]

% HPCA Exit / HPCR Inlet (Station 2)
Po2 = 425460;                  % Stagnation pressure [Pa]
To2 = 491.086;                 % Stagnation temperature [K]
% HPCR Exit / Burner Inlet (Station 3)
Po3 = 1276380;                 % Stagnation pressure [Pa]
To3 = 723.524;                 % Stagnation temperature [K]

% Design choices
Pr_total = Po2/P0_1m;                           % Overall pressure ratio
e_c = 0.79;                                     % Polytropic efficiency
Tr_total = Pr_total^((gamma-1)/(e_c*gamma));    % Overall temperature ratio 
num_stages = 3;                                 % Number of stages (design input)
export_blade_files = false;                     % Write stator/rotor_outline_stage.txt from bladeGen_2D
deHaller_min = 0.72;                            % Minimum acceptable De Haller ratio
min_reynolds = 300000;                          % Minimum reynolds number
kin_visc = 1.46e-5;                             % From chart, 0km
solidity_rotor = 1;
solidity_stator = 1.25;
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

% Inlet annulus sized from continuity, so geometric area = continuity area for ANY httrr
m_dot = mdot_core;                              % Core mass flow [kg/s]
A1_Cont = m_dot/(rho_1m*z_1m);                  % Annulus area required [m^2]
r_tip_1 = sqrt(A1_Cont/(pi*(1-httrr^2)));       % Tip radius [m]
r_hub_1 = r_tip_1*httrr;                        % Hub radius [m]
A_1 = (r_tip_1^2 - r_hub_1^2)*pi;              
A1_Geo = A_1;                                   % Annulus area from geometry [m^2]

% Wheel speed / tip speed (one of the two is fixed, the other follows from r_tip_1)
if fix_speed == "rpm"
    omega = N*pi/30;                            % Wheel speed [rad/s]
    U_tip_1 = omega*r_tip_1;                    % Tip speed [m/s]
else
    U_tip_1 = Mu_1t_max*a_1m;                   % Tip speed [m/s]
    omega = U_tip_1/r_tip_1;                    % Wheel speed [rad/s]
    N = omega*30/pi;                            % Shaft speed [rpm]
end
Mu_1t = U_tip_1/a_1m;                           % Resulting tip tangential Mach number
m_dot_geo = rho_1m*z_1m*A_1;                    % Mass flow (geometry) [kg/s]

%% Compressor exit conditions
% Meanline
P0_exit_m = P0_1m * Pr_total; % Exit stagnation Pressure [Pa]
T0_exit_m = T0_1m * Tr_total; % Exit stagnation Temperature [K]

alpha_exit_m = alpha_1m;  % repeating stage [degrees]
z_exit_m = z_1m;          % Constant Axial Velocity, design choice
C_exit_m = C_1m;          

T_exit_m = T0_exit_m - C_exit_m^2/(2*cp); % Exit static Temperature [K]

a_exit_m = sqrt((gamma-1)*cp*T_exit_m);
Mz_exit_m = z_exit_m/a_exit_m;
Mc_exit_m = Mz_exit_m/cosd(alpha_exit_m);

P_exit_m = P0_exit_m/(1+(gamma-1)*Mc_exit_m^2/2)^(gamma/(gamma-1)); 
rho_exit_m = P_exit_m/(R*T_exit_m);

% Exit annulus geometry
A_exit = m_dot/rho_exit_m/z_exit_m;

syms h
r_mean_1 = (r_tip_1 + r_hub_1)/2;
h = double(solve((r_mean_1+h)^2 - (r_mean_1-h)^2 == A_exit/pi, h));

r_hub_exit = r_mean_1 - h;
r_tip_exit = r_mean_1 + h;

%% Pitchline calculations
ang_vel = omega;  % rad/s (U_tip_1/r_tip_1)
rpm = N;

% Station 1 - Meanline
U_1m = U_tip_1 * (r_mean_1/r_tip_1);
beta_1m = atand((U_1m-z_1m*tand(alpha_1m))/z_1m);
W_1m = z_1m / cosd(beta_1m);
Ctheta_1m = z_1m*tand(alpha_1m);
Wtheta_1m = U_1m - Ctheta_1m;

Mw_1m = W_1m/a_1m;

% Station 2 - Meanline
U_2m = U_1m;  % Initial Approximation, true if we adjust both hub and shroud
z_2m = z_1m;  % Design choice

% Stage loading is set by the number of stages (Euler work equation):
% cp*dT0_stage = U*(Ctheta_2 - Ctheta_1)
temp_rise_total = T0_exit_m - T0_1m;
temp_rise_per_stage = temp_rise_total/num_stages;
Ctheta_2m = Ctheta_1m + cp*temp_rise_per_stage/U_1m;
Wtheta_2m = U_2m - Ctheta_2m; % signed, can be negative at high loading
W_2m = sqrt(z_2m^2 + Wtheta_2m^2);
beta_2m = atand(Wtheta_2m/z_2m); % signed
C_2m = sqrt(z_2m^2 + Ctheta_2m^2);
alpha_2m = atand(Ctheta_2m/z_2m);
deHaller_actual = W_2m/W_1m; % now an output, checked against deHaller_min

phi_2m = z_2m/U_2m; % Flow Coefficient 
psi_2m = 1 + phi_2m*(tand(-beta_2m)-tand(alpha_1m)); % Loading Coefficient

% Station 3 
C_3m = C_1m;
W_3m = W_1m;
U_3m = U_1m;
z_3m = z_1m;
Ctheta_3m = Ctheta_1m;
Wtheta_3m = Wtheta_1m;
alpha_3m = alpha_1m;
beta_3m = beta_1m;

phi_3m = z_3m/U_3m; % Flow Coefficient 

% Stage metrics
degR_m = 1 - (Ctheta_1m + Ctheta_2m) / (2*U_1m); % Degree of reaction
% Diffusion Factor Rotor
D_mr = D_factor(W_1m, W_2m, Ctheta_1m, Ctheta_2m, solidity_rotor);
% Diffusion Factor Stator
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
temp_rise_per_stage = T0_2m - T0_1m; % equals total/num_stages by construction
num_stages_actual = temp_rise_total/temp_rise_per_stage;
num_stations = num_stages*2 + 1;

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
free_vortex_valid = isreal(FF.r_hub_vec_full) && isreal(FF.r_tip_vec_full);

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
nexttile
hold on
title("Annulus geometry")
x_axis = 1:1:num_stages+1;
x_axis = (x_axis-1) * 2 * chord_m;
plot(x_axis, [r_hub_vec', r_tip_vec'], '.-r')
plot(x_axis, [-r_hub_vec', -r_tip_vec'], '.-r')
x_axis_long = 1:1:FF.num_stations;
x_axis_long = (x_axis_long-1) * chord_m;
plot(x_axis_long, real([FF.r_hub_vec_full', FF.r_tip_vec_full']), '.-k')
plot(x_axis_long, real([-FF.r_hub_vec_full', -FF.r_tip_vec_full']), '.-k')
ylim([-max(r_tip_vec)*1.2,max(r_tip_vec)*1.2])
xlim([x_axis(1), x_axis(end)])
pbaspect([max(x_axis)-min(x_axis),2*max(r_tip_vec)*1.2,1])
grid minor
xlabel("z (m)")
ylabel("r (m)")

plot_spanwise_distributions(num_stages, num_stations, chord_m, r_mean_1, r_hub_vec, r_tip_vec, FF)

%% 2D Blade Generation (MCA) and Cascade Plots -- one bladeGen_2D call per stage
% Inputs per stage k (read from the free-vortex stations at span fraction span_frac):
%   beta_rotor_in(k)   : rotor inlet relative flow angle   (station 2k-1 of the stage)
%   alpha_stator_in(k) : stator inlet absolute flow angle  (station 2k, rotor exit)
span_frac = 0.5;                                % 0 = hub, 0.5 = meanline, 1 = tip
n_blades_plot = 3;                              % Blades drawn per row in the cascade plots
beta_rotor_in   = zeros(1, num_stages);         % deg
alpha_stator_in = zeros(1, num_stages);         % deg
idx_span = round(1 + span_frac*(FF.num_streamlines-1));
for k = 1:num_stages
    if free_vortex_valid
        st_in  = 2*k - 1;                       % rotor inlet station
        st_mid = 2*k;                           % rotor exit / stator inlet station
        r_in   = FF.r_spans{st_in}(idx_span);
        Ct_in  = FF.Ctheta_spans{st_in}(idx_span);
        z_in   = FF.z_spans{st_in}(idx_span);
        Ct_mid = FF.Ctheta_spans{st_mid}(idx_span);
        z_mid  = FF.z_spans{st_mid}(idx_span);
        beta_rotor_in(k)   = atand((ang_vel*r_in - Ct_in)/z_in);
        alpha_stator_in(k) = atand(Ct_mid/z_mid);
    else                                        % fall back to the repeating-stage meanline angles
        beta_rotor_in(k)   = beta_1m;
        alpha_stator_in(k) = alpha_2m;
    end
    blades(k) = bladeGen_2D(alpha_stator_in(k), -beta_rotor_in(k), solidity_rotor, solidity_stator, ...
        'chord_mm', chord_m*1000, 'export_files', export_blade_files, ...
        'file_tag', sprintf("_stage%d", k));
end
% Figures 3 (rotor cascades),4 (stator cascades), 5 (HPCA stages)
plot_blade_stages(blades, n_blades_plot, 2)

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
fprintf("    Polytropic Efficiency:            %12.3f\n",       e_c)
fprintf("    Rotor Diffusion Factor:           %12.3f\n",       rps.D_mr)
fprintf("    Stator Diffusion Factor:          %12.3f\n",       rps.D_ms)
fprintf("    Stage Degree of Reaction:         %12.3f\n",       rps.degR_m)
fprintf("    De Haller Ratio (actual):         %12.3f\n",       deHaller_actual)
fprintf("    Rotor Inlet Mach Number:          %12.3f\n",       Mw_1m)
fprintf("    Stator Inlet Mach Number:         %12.3f\n",       Mc_2m)
fprintf("    Compressor Inlet Mach Number:     %12.3f\n",       Mc_1m)
fprintf("    Compressor Outlet Mach Number:    %12.3f\n",       Mc_exit_m)
fprintf("Triangles:\n")
fprintf("    Rotor Turning:                    %12.3f deg\n",   abs(beta_2m - beta_1m))
fprintf("    Stator Turning:                   %12.3f deg\n",   abs(alpha_1m - alpha_2m))
fprintf("Misc:\n")
fprintf("    Number of Stages (input):         %12.3f\n",       num_stages)
fprintf("    Blade Chord Length:               %12.3f m\n",     chord_m)
fprintf("    RPM:                              %12.3f rpm\n",   rpm)
fprintf("    Hub to Tip Ratio:                 %12.3f\n",       httrr)
fprintf("    Inlet Tip Tangential Mach:        %12.3f\n",       Mu_1t)
fprintf("    Mass Flow (core):                 %12.3f kg/s\n",  m_dot)
fprintf("    Inlet Tip Diameter:               %12.3f mm\n",    real(FF.r_tip_vec_full(1))*2*1000)
fprintf("Blade Generation (MCA), per stage (span fraction %.2f):\n", span_frac)
for k = 1:num_stages
    fprintf("    Stage %d: rotor inlet beta = %8.3f deg, stator inlet alpha = %8.3f deg\n", k, beta_rotor_in(k), alpha_stator_in(k))
    fprintf("        Rotor : stagger %8.3f | camber %8.3f | deviation %8.3f | deflection %8.3f deg\n", ...
        blades(k).rotor.stagger, blades(k).phi_R, blades(k).delta_R, blades(k).epsilon_R)
    fprintf("        Stator: stagger %8.3f | camber %8.3f | deviation %8.3f | deflection %8.3f deg\n", ...
        blades(k).stator.stagger, blades(k).phi_S, blades(k).delta_S, blades(k).epsilon_S)
end
fprintf("Continuity Check (inlet annulus):\n")
fprintf("    Area required (continuity):       %12.6f m^2\n",   A1_Cont)
fprintf("    Area from geometry:               %12.6f m^2\n",   A1_Geo)
fprintf("    Mass flow through geometry:       %12.3f kg/s\n",  m_dot_geo)
fprintf("\n======== Warnings ========\n")
if abs(A1_Cont - A1_Geo)/A1_Cont > 0.01
    fprintf("    Inlet annulus area differs from continuity requirement by more than 1%%.\n")
end
if ~free_vortex_valid
    fprintf("    Free-vortex spanwise solution is complex (axial velocity squared < 0 near the tip).\n")
    fprintf("    Stage loading is too high for this annulus: increase num_stages or httrr.\n")
end
if Mu_1t > Mu_1t_max
    fprintf("    Inlet tip tangential Mach %.3f exceeds the limit of %.2f.\n", Mu_1t, Mu_1t_max)
end
if deHaller_actual < deHaller_min
    fprintf("    Rotor De Haller ratio %.3f is below the minimum of %.2f.\n", deHaller_actual, deHaller_min)
end
if rps.D_mr > 0.6 || rps.D_ms > 0.6
    fprintf("    Diffusion factor above ~0.6 (rotor %.3f, stator %.3f).\n", rps.D_mr, rps.D_ms)
end
if Mc_2m > 1
    fprintf("    Stator inlet Mach number %.3f is supersonic.\n", Mc_2m)
end

%% Functions
function D = D_factor(W1, W2, Ctheta_1, Ctheta_2, sigma)
    % Diffusion factor, generally kept below ~0.55-0.6 to prevent boundary layer separation
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

function plot_blade_stages(blades, n_blades, fig_base)
    % Rotor cascades, stator cascades (one tile per stage) and the full multi-stage HPCA plot
    n = numel(blades);
    col_R = [0 0.4470 0.7410];
    col_S = [0.8500 0.3250 0.0980];

    % Rotor cascades
    figure(fig_base+1); clf;
    tiledlayout(1, n, TileSpacing='compact', Padding='compact')
    for k = 1:n
        nexttile; hold on
        for j = 0:n_blades-1
            plot(blades(k).foil_R(1,:), blades(k).foil_R(2,:) + j*blades(k).pitch_R, 'Color', col_R)
        end
        hold off
        xlabel("Axial Direction ($z$)", 'Interpreter','latex');
        ylabel("Tangential Direction ($\theta$)", 'Interpreter','latex');
        title(sprintf("Rotor Cascade, Stage %d: Stagger = %.2f°, Solidity = %.2f", ...
            k, blades(k).rotor.stagger, 1/blades(k).pitch_R))
        axis equal; grid on
    end

    % Stator cascades
    figure(fig_base+2); clf;
    tiledlayout(1, n, TileSpacing='compact', Padding='compact')
    for k = 1:n
        nexttile; hold on
        for j = 0:n_blades-1
            plot(blades(k).foil_S(1,:), blades(k).foil_S(2,:) + j*blades(k).pitch_S, 'Color', col_S)
        end
        hold off
        xlabel("Axial Direction ($z$)", 'Interpreter','latex');
        ylabel("Tangential Direction ($\theta$)", 'Interpreter','latex');
        title(sprintf("Stator Cascade, Stage %d: Stagger = %.2f°, Solidity = %.2f", ...
            k, blades(k).stator.stagger, 1/blades(k).pitch_S))
        axis equal; grid on
    end

    % Full HPCA, all stages in series
    figure(fig_base+3); clf; hold on
    x_off = 0;
    x_label = zeros(1, n);
    for k = 1:n
        b = blades(k);
        for j = 0:n_blades-1
            plot(b.foil_R(1,:) + x_off,           b.foil_R(2,:) + j*b.pitch_R, 'Color', col_R)
            plot(b.foil_S(1,:) + x_off + b.x_shift, b.foil_S(2,:) + j*b.pitch_S, 'Color', col_S)
        end
        x_label(k) = x_off + b.x_shift/2;
        if k < n   % next stage's rotor starts one gap after this stator
            x_off = x_off + b.x_shift + max(b.foil_S(1,:)) + b.gap - min(blades(k+1).foil_R(1,:));
        end
    end
    h_R = plot(nan, nan, 'Color', col_R);
    h_S = plot(nan, nan, 'Color', col_S);
    axis equal; grid on
    yl = ylim;
    for k = 1:n
        text(x_label(k), yl(1), sprintf("Stage %d", k), 'HorizontalAlignment','center', 'VerticalAlignment','bottom')
    end
    hold off
    legend([h_R h_S], {'Rotor', 'Stator'}, 'Location', 'best')
    xlabel("Axial Direction ($z$)", 'Interpreter','latex');
    ylabel("Tangential Direction ($\theta$)", 'Interpreter','latex');
    title(sprintf("HPCA - %d Stages", n))
end
