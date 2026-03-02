% CEA_ROCKET_EXAMPLE: Example file for the MATLAB CEA wrapper. For in-depth
% documentation read the headers of cea_rocket_run.m,
% cea_rocket_run_single.m, and cea_rocket_read.m

% Change this variable to true to rerun CEA instead of using saved values
CEA_RUN = true;
CEA_SAVE_FILE = 'cea_high_isp.mat';

% The CEA MATLAB code takes a MATLAB map (called a dictionary in Python or
% hash in C) as input. The dictionary uses MATLAB character arrays as the
% keys, and the value data type varies by which key is used. Details of
% each key are listed in cea_rocket_run.m
% For example: inp('key') = value.
inp = containers.Map;
inp('type') = 'eq fr';              % Sets the type of CEA calculation
inp('p') = 500;                % Chamber pressure
inp('p_unit') = 'psi';              % Chamber pressure units
inp('o/f') = 0.8:0.1:1.2;               % Mixture ratio
inp('pip') = inp('p')/0.1;               % Supersonic area ratios
% inp('pip') = [5];                   % Pressure ratios
inp('fuel') = {'Li(L)', 'H2'};             % Fuel name from thermo.inp
inp('fuel_wt%') = [37, 63];             % Fuel name from thermo.inp
inp('fuel_t') = [298+200, 298];                % Fuel inlet temperature
inp('ox') = {'F2', 'He'};              % Ox name from thermo.inp
inp('ox_wt%') = [95, 5];             % Fuel name from thermo.inp
inp('ox_t') = [298, 298];                  % Ox inlet temperature
% inp('file_name') = 'H2O2_T.inp';    % Input/output file name
if CEA_RUN
    data = cea_rocket_run(inp);     % Call the CEA MATLAB code
    save(CEA_SAVE_FILE, 'data');
else
    load(CEA_SAVE_FILE);
end

% The output data structure, called 'data' in this case, is also a MATLAB
% map. 'data' contains a single entry for each of the CEA calculation types
% listed ('eq' and 'fr'). For instance, if only 'fr' is listed, then 'data'
% will only contain a single entry under data('fr').
data_eq = data('eq');
data_fr = data('fr');

% Use keys(data_eq) or keys(data_fr) to see the contents of each map
% respectively. Every output of CEA is contained in these keys, including
% molar concentrations. Most keys contain a 3D array with columns
% corresponding to the pressure, O/F, and area/pressure ratio inputs
% respectively. If only a single value is given for one of these inputs,
% the output will still be a 3D array. The squeeze() MATLAB function must
% be used to reduce the number of dimensions appropriately. Read the notes
% at the top of cea_rocket_read.m for more details.
temperature = squeeze(data_eq('t'));
isp = squeeze(data_eq('isp'));
ivac = squeeze(data_eq('ivac'));