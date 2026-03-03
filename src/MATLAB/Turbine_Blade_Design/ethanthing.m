clear;clc;

%% Design Variables:
% x(1) -> Cx  = axial chord
% x(2) -> ttc = thickness/chord ratio
% x(3) -> N_B = number of blades

% Objective 1: Zweifel
% Objection 2: Curvature

%% Design Variable Bounds
Cx_bounds  = [5, 30];
ttc_bounds = [10, 25];
N_B_bounds = [13, 37];

num_samples = 1000;
lhs = lhsdesign(num_samples,3);

Cx_space  = lhs(:,1) .* range(Cx_bounds)  + Cx_bounds(1);
ttc_space = lhs(:,2) .* range(ttc_bounds) + ttc_bounds(1);
N_B_space = lhs(:,3) .* range(N_B_bounds) + N_B_bounds(1);

%% ========= STATIC INPUTS (NON-DESIGN VARIABLES) ============
% Inputs are for rotor for now
R = 50;                 % Tip Radius                i| mm
R_LE = 0.8;             % Leading edge radius       i| mm
R_TE = 0.6;             % Trailing edge radius      i| mm

% Design Variable - ttc % Thickness to Chord ratio  i| %
% Design Variable - Cx  % Axial chord               i| mm
zeta = 0.01;            % Unguided turning angle    i| degrees
beta_IN = 23.67;        % Inlet blade angle         i| degrees
ep_IN = 10;             % Inlet half wedge angle    i| degrees
beta_OUT = -51;         % Exit blade angle          i| degrees
ep_OUT = zeta/2;        % Exit half wedge angle     u| degrees

% Design Variable - N_B % Number of blades          i| N/A
blade_height = 10.43;   % Height of blade           i| mm
V_mag_mid = 277;
% ============================================================





max_curvature = ones([1,num_samples]);
average_zweifel = ones([1,num_samples]);

%% TIME/FIDELITY CONTROLS
resolution = 1;
iteration_threshold = 0.1;
counter = [];

for i = 1:num_samples
    blade_params =  IFN.blade_parameters(R, R_LE, R_TE, Cx_space(i), ttc_space(i), zeta, beta_IN, ep_IN, beta_OUT, ep_OUT, N_B_space(i), blade_height, V_mag_mid, "Rotor", resolution, iteration_threshold);
    [blade, ~, success] = IFN.generate_blade(blade_params, 0);
    if success == false
        counter(end+1) = i;
        continue
    end
    max_curvature(i) = max([blade([2, 3, 4]).k_max_ss]);
    zweifels = [blade(2).parameters.zweifel, blade(3).parameters.zweifel, blade(4).parameters.zweifel];
    average_zweifel(i) = mean(zweifels);
    fprintf("Sample# %i\n", i)
end

counterCounter = 0;
for i = counter
    max_curvature(i-counterCounter) = [];
    average_zweifel(i-counterCounter) = [];
    Cx_space(i-counterCounter) = [];
    ttc_space(i-counterCounter) = [];
    N_B_space(i-counterCounter) = [];
    counterCounter = counterCounter + 1;
end

fprintf("Final Number of Blades Plotted: %i", length(Cx_space))

zweifel_target = 1;
abs_dist_targetZweifel = abs(average_zweifel-zweifel_target);

range_curvature = range(max_curvature);
range_zweifel = range(average_zweifel);
range_targetZweifel = range(abs_dist_targetZweifel);
min_curvature = min(max_curvature);
min_zweifel = min(average_zweifel);
min_targetZweifel = min(abs_dist_targetZweifel);

norm_maxCurvature = (max_curvature-min_curvature)./range_curvature;
norm_averageZweifel = (average_zweifel-min_zweifel)./range_zweifel;
norm_targetZweifel = (abs_dist_targetZweifel-min_targetZweifel)./range_targetZweifel;

%% Weights
zweifel_weight = 0.5;
curvature_weight = 0.5;

fitness = curvature_weight .* norm_maxCurvature + zweifel_weight .* norm_targetZweifel;

%% Unaltered Design Space
% Create Figure
figure(1)
hold on
tiledlayout(1,3, TileSpacing='tight', Padding='tight')
nexttile
scatter3(Cx_space, ttc_space, N_B_space, 10, max_curvature, 'filled')
title("Max Curvature")
xlabel("Axial Chord")
ylabel("Thickness to Chord Ratio")
zlabel("Number of Blades")
colorbar

nexttile
scatter3(Cx_space, ttc_space, N_B_space, 10, average_zweifel, 'filled')
title("Average Zweifel")
xlabel("Axial Chord")
ylabel("Thickness to Chord Ratio")
zlabel("Number of Blades")
colorbar

nexttile
scatter3(Cx_space, ttc_space, N_B_space, 10, fitness, 'filled')
title("Fitness")
xlabel("Axial Chord")
ylabel("Thickness to Chord Ratio")
zlabel("Number of Blades")
colorbar

%% Normalized Plots
figure(2)
hold on
tiledlayout(1,3, TileSpacing='tight', Padding='tight')
nexttile
scatter3(Cx_space, ttc_space, N_B_space, 10, norm_maxCurvature, 'filled')
title("Normalized Max Curvature")
xlabel("Axial Chord")
ylabel("Thickness to Chord Ratio")
zlabel("Number of Blades")
colorbar

nexttile
scatter3(Cx_space, ttc_space, N_B_space, 10, norm_targetZweifel, 'filled')
title("Normalized Average Zweifel")
xlabel("Axial Chord")
ylabel("Thickness to Chord Ratio")
zlabel("Number of Blades")
colorbar

nexttile
scatter3(Cx_space, ttc_space, N_B_space, 10, abs_dist_targetZweifel, 'filled')
title("Normalized Target Zweifel")
xlabel("Axial Chord")
ylabel("Thickness to Chord Ratio")
zlabel("Number of Blades")
colorbar


% figure(3)
% hold on
% tiledlayout(1,1, TileSpacing='tight', Padding='tight')
% nexttile
% scatter3(Cx_space, ttc_space, N_B_space, 10, fitness, 'filled')
% title("Fitness")
% xlabel("Axial Chord")
% ylabel("Thickness to Chord Ratio")
% zlabel("Number of Blades")
% colorbar