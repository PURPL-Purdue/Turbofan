clear;clc;clf;

% ==== STATIC INPUTS (NON-DESIGN VARIABLES) ====
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

%% TIME/FIDELITY CONTROLS
resolution = 1;
iteration_threshold = 0.1;

%% PLOTTING CONTROLS
type = "rotor";        % Type of blade we're doing
plot_throat = true;     % Set "true" to display the throat lines
plot_t_max  = true;     % Set "true" to display the maximum airfoil thickness lines
plot_spline_controls = false;    % Set "true" to display the P0 -> P1 and P1 -> P2 lines
LE_align = true;        % Set "true" to align the leading edges
show_curvature = false;
flip_stator = true;
num_blades  = 1;        % Number of rotors to display, minimum 3

%% DESIGN VARIABLES:
% x(1) -> Cx  = axial chord
% x(2) -> ttc = thickness/chord ratio
% x(3) -> N_B = number of blades

%% OBJECTIVES
% Objective 1: Zweifel
% Objection 2: Curvature


%% =========== MAIN =========== %%
objFuns = @objectives;

opts_ps = optimoptions('paretosearch','Display','off','PlotFcn','psplotparetof');
rng default % For reproducibility

Aineq       = [];
bineq       = [];
Aeq         = [];
beq         = [];
lb          = [10,5,13];
ub          = [25,30,35];
nonLinCon   = [];

[x_inputs,obj_results,~,psoutput1] = paretosearch(objFuns,3,Aineq,bineq,Aeq,beq,lb,ub,nonLinCon,opts_ps);

load gong.mat;
soundsc(y); % Gggggongongongongongong

%% TARGET ZWEIFEL
indexed_obj_results = [obj_results, [1:1:length(obj_results)]'];
bad_bool = obj_results(:,1) > 0.16;
% bad_bool = isoutlier(obj_results(:,1));

counter = 0;
for i = 1:length(bad_bool)
    if bad_bool(i) == 1
        indexed_obj_results(i-counter,:) = [];
        counter = counter + 1;
    end
end

[~, min_pseudo_index] = min(indexed_obj_results(:,2));
min_dist_index = indexed_obj_results(min_pseudo_index,3);

%% PLOTTING
figure(1)
for i = 1:length(x_inputs)    
    blade_params =  IFN.blade_parameters(R, R_LE, R_TE, x_inputs(i,1), x_inputs(i,2), zeta, beta_IN, ep_IN, beta_OUT, ep_OUT, x_inputs(i,3), blade_height, V_mag_mid, "Rotor", resolution, iteration_threshold);
    [blade, ~, success] = IFN.generate_blade(blade_params, 0);
    if success == false
        fprintf("huh?!!?!?")
    else
        if i == min_dist_index
            plotSingle(blade, type, plot_throat, plot_t_max, plot_spline_controls, LE_align, show_curvature, flip_stator, num_blades, 3, 3, "highlight")
        else
            plotSingle(blade, type, plot_throat, plot_t_max, plot_spline_controls, LE_align, show_curvature, flip_stator, num_blades, 3, 3, "regular")
        end
    end
end

figure(3)
blade_params =  IFN.blade_parameters(R, R_LE, R_TE, x_inputs(min_dist_index,1), x_inputs(min_dist_index,2), zeta, beta_IN, ep_IN, beta_OUT, ep_OUT, x_inputs(min_dist_index,3), blade_height, V_mag_mid, "Rotor", resolution, iteration_threshold);
[blade, ~, success] = IFN.generate_blade(blade_params, 0);
if success == false
    fprintf("huh?!!?!?")
else
    plotSingle(blade, type, plot_throat, plot_t_max, plot_spline_controls, LE_align, show_curvature, flip_stator, num_blades, 3, 3, "regular")
end
% IFN.gong

%% OBJECTIVE FUNCTIONS
function F = objectives(x)
    % ==== STATIC INPUTS (NON-DESIGN VARIABLES) ====
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
    
    num_elements = length(x(:,1));

    % max_curvature = ones([1,num_elements]);
    % average_zweifel = ones([1,num_elements]);

    %% TIME/FIDELITY CONTROLS
    resolution = 1;
    iteration_threshold = 0.1;
    
    blade_params =  IFN.blade_parameters(R, R_LE, R_TE, x(1), x(2), zeta, beta_IN, ep_IN, beta_OUT, ep_OUT, x(3), blade_height, V_mag_mid, "Rotor", resolution, iteration_threshold);
    [blade, ~, success] = IFN.generate_blade(blade_params, 0);
    if success == false
        max_curvature = 10;
        average_zweifel = 10;
    else
        max_curvature = max([blade([2, 3, 4]).k_max_ss]);
        zweifels = [blade(2).parameters.zweifel, blade(3).parameters.zweifel, blade(4).parameters.zweifel];
        average_zweifel = mean(zweifels);
    end
    % fprintf("Sample# %i\n", i)
    
    target_zweifel = abs(average_zweifel - 1);

    F = [max_curvature, target_zweifel];
end