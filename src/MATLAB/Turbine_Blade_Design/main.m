clear;clc;clf;
folder = fileparts(fileparts(mfilename('fullpath')));
addpath(fullfile(folder,'Blade_Design\', 'Pritchard_Functions'))
addpath(fullfile(folder,'Blade_Design\', 'Plotting'))

%% STATOR INPUTS
% (The column of numbers that starts with 5.5 contain the sample values given in the Pritchard paper)
S_R = 50;               % Tip Radius                i| mm           5.5
S_R_LE = 1.4;           % Leading edge radius       i| mm           0.031
S_R_TE = 0.7;           % Trailing edge radius      i| mm           0.016

S_ttc = 16.06;             % Thickness to Chord ratio  i| %            N/A
S_Cx = 23.56;              % Axial chord               i| mm           1.102              
S_zeta = 0.01;          % Unguided turning angle    i| degrees      6.3
S_beta_IN = 0;          % Inlet blade angle         i| degrees      35
S_ep_IN = 8;            % Inlet half wedge angle    i| degrees      8
S_beta_OUT = -64.48;       % Exit blade angle          i| degrees      -57
S_ep_OUT = S_zeta/2;    % Exit half wedge angle     u| degrees      3.32

S_N_B = 13;             % Number of blades          i| N/A          51 
S_blade_height = 11;    % Height of blade           i| mm           N/A

S_V_mag_mid = 525;

%% ROTOR INPUTS
% (The column of numbers that starts with 5.5 contain the sample values given in the Pritchard paper)
T_R = 50;               % Tip Radius                i| mm           5.5
T_R_LE = 0.8;           % Leading edge radius       i| mm           0.031
T_R_TE = 0.6;           % Trailing edge radius      i| mm           0.016

T_ttc = 12.4375;             % Thickness to Chord ratio  i| %            N/A
T_Cx = 14.6875;              % Axial chord               i| mm           1.102
T_zeta = 0.01;          % Unguided turning angle    i| degrees      6.3
T_beta_IN = 23.67;        % Inlet blade angle         i| degrees      35
T_ep_IN = 10;           % Inlet half wedge angle    i| degrees      8
T_beta_OUT = -51;       % Exit blade angle          i| degrees      -57
T_ep_OUT = T_zeta/2;    % Exit half wedge angle     u| degrees      3.32

T_N_B = 25.375;             % Number of blades          i| N/A          51 
T_blade_height = 11;    % Height of blade           i| mm           N/A

T_V_mag_mid = 277;

%% PLOTTING CONTROLS
plot_throat = true;     % Set "true" to display the throat lines
plot_t_max  = true;     % Set "true" to display the maximum airfoil thickness lines
plot_spline_controls = false;    % Set "true" to display the P0 -> P1 and P1 -> P2 lines
LE_align = true;        % Set "true" to align the leading edges
show_curvature = false;
flip_stator = true;

plot_optimized_stator = false;  % Set "true" to search directory for blades of max fitness and plot those
plot_optimized_rotor  = false;  % Set "true" to search directory for blades of max fitness and plot those
evo_to_search = 2;

num_stators = 2;        % Number of stators to display, minimum 3
num_rotors  = 2;        % Number of rotors to display, minimum 3
num_fluent  = 3;        % Number of blade profiles to export for ansys fluent

num_interpolate = 0;

%% TIME/FIDELITY CONTROLS
resolution = 10;
iteration_threshold = 0.1;

%% MAIN
% if plot_optimized_stator
%     stator_best_inputs = get_best(evo_to_search, "stator");
%     stator_params = blade_parameters(S_R, S_R_LE, S_R_TE, stator_best_inputs(2), stator_best_inputs(1), S_zeta, S_beta_IN, S_ep_IN, S_beta_OUT, S_ep_OUT, stator_best_inputs(3), S_blade_height, S_V_mag_mid, "Stator");
% else
stator_params = IFN.blade_parameters(S_R, S_R_LE, S_R_TE, S_Cx, S_ttc, S_zeta, S_beta_IN, S_ep_IN, S_beta_OUT, S_ep_OUT, S_N_B, S_blade_height, S_V_mag_mid, "Stator", resolution, iteration_threshold);
% end
% 
% if plot_optimized_rotor
%     rotor_best_inputs = get_best(evo_to_search, "rotor");
%     rotor_params =  blade_parameters(T_R, T_R_LE, T_R_TE, rotor_best_inputs(2), rotor_best_inputs(1), T_zeta, T_beta_IN, T_ep_IN, T_beta_OUT, T_ep_OUT, rotor_best_inputs(3), T_blade_height, T_V_mag_mid, "Rotor");
% else
rotor_params =  IFN.blade_parameters(T_R, T_R_LE, T_R_TE, T_Cx, T_ttc, T_zeta, T_beta_IN, T_ep_IN, T_beta_OUT, T_ep_OUT, T_N_B, T_blade_height, T_V_mag_mid, "Rotor", resolution, iteration_threshold);
% end

% Stuff (math)
[stator_blade, mid_profile_index, ~] = IFN.generate_blade(stator_params, num_interpolate);
[rotor_blade, ~, ~]  = IFN.generate_blade(rotor_params, num_interpolate);

% Create Figure
figure(1)
tiledlayout(1,4, TileSpacing='tight', Padding='tight')
nexttile
title("Full Blade")
plotSet(rotor_blade, stator_blade, plot_throat, plot_t_max, plot_spline_controls, LE_align, show_curvature, flip_stator, num_stators, num_rotors, 2:length(rotor_blade)-1, mid_profile_index)
nexttile
title("Hub Profiles")
plotSet(rotor_blade, stator_blade, plot_throat, plot_t_max, plot_spline_controls, LE_align, show_curvature, flip_stator, num_stators, num_rotors, 2, 2)
nexttile
title("Mid Profiles")
plotSet(rotor_blade, stator_blade, plot_throat, plot_t_max, plot_spline_controls, LE_align, show_curvature, flip_stator, num_stators, num_rotors, mid_profile_index, mid_profile_index)
nexttile
title("Tip Profiles")
plotSet(rotor_blade, stator_blade, plot_throat, plot_t_max, plot_spline_controls, LE_align, show_curvature, flip_stator, num_stators, num_rotors, length(rotor_blade)-1, length(rotor_blade)-1)

% Export profiles for Solidworks and Ansys
export(rotor_blade, stator_blade, LE_align, mid_profile_index, mid_profile_index)

% Print Selected Info
fprintf("\nINFO: -------------------------------\n\n")
for i = 1:3
    fprintf(stator_blade(i).parameters.name + "\n")
    fprintf("   Zweifel: " + stator_blade(i).parameters.zweifel + "\n")
    fprintf("   T_max: " + stator_blade(i).parameters.t_max + "\n")
    fprintf("   K_max_ss: " + stator_blade(i).k_max_ss + "\n")
end
fprintf("\n")
for i = 1:3
    fprintf(rotor_blade(i).parameters.name + "\n")
    fprintf("   Zweifel: " + rotor_blade(i).parameters.zweifel + "\n")
    fprintf("   T_max: " + rotor_blade(i).parameters.t_max + "\n")
    fprintf("   K_max_ss: " + rotor_blade(i).k_max_ss + "\n")
end