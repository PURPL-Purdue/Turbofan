function [data] = cea_rocket_run(inp, data)
%CEA_ROCKET_RUN CEA wrapper that accounts for CEAs input limitations for
%   pressure, mixture, and ratio.
%
% Input (General)
%   inp: A containers.Map datatype containing the CEA input parameters.
%   data: A containers.Map that returns the CEA output data. See the
%       'cea_rocket_read.m' help string for details.
%   inp('file_name'): The file name used for the generated input and output
%       files. If not specified, a random file name will be used and the
%       input/output files will be deleted after use. If a file name is
%       specified with this parameter, the input/output files will not be
%       deleted. When multiple files have to be generated, the iteration
%       number is appended to the file name base such that they can all be
%       retrieved at the end of the run.
%   inp('type'): The type of CEA analysis. Typically use either 'eq', 'fr',
%       or 'eq fr'. Can also input other parameters here like 'ions'.
%   inp('mdot'): Finite area combustor mass flow rate to chamber area
%       ratio in (kg/s/m^2). An infinite area combustor assumption is used
%       if neither inp('mdot') nor inp('ac') are set. Frozen flow does not
%       work with a finite area combustor. This is a CEA limitation.
%   inp('ac'): Finite area combustor contraction ratio. An infinite area
%       combustor assumption is used if neither inp('mdot') nor inp('ac')
%       are set. Frozen flow does not work with a finite area combustor.
%       This is a CEA limitation.
%   inp('omit'): Cell list of char arrays listing species to omit from the
%       calculation. Can also input a single char array to omit only one
%       specie. Often used for condensed species when operating with nozzle
%       exit area ratios near the boiling points of such species.
%
% Input (Rocket Parameters)
%   inp('p'): An array of pressures (or a single pressure) used as the CEA
%       chamber pressure. The default unit is bar.
%   inp('p_unit'): The units used for 'p'. See the CEA manual for valid
%       options. As a starting point, 'bar' and 'psi' are valid, but 'Pa'
%       is not.
%   inp('o/f'): Array of O/Fs (or a single O/F) used as the CEA mixture
%       ratio. Can not be specified at the same time as inp('phi').
%   inp('phi'): Array of phis (or a single phi) used as the CEA mixture
%       ratio. Can not be specified at the same time as inp('o/f').
%   inp('sup'): Array of supersonic area ratios (or a single one). Can not
%       be specified at the same time as inp('pip').
%   inp('sub'): Array of subsonic area ratios (or a single one). Can not be
%       specified at the same time as inp('pip').
%   inp('pip'): Array of Pinfinity/P (or a single one). Can not be
%       specified at the same time as inp('sup') or inp('sub').
%
% Input (Reactants)
%   inp('fuel'): Array of fuel names (or a single one). Each fuel name must
%       be in the thermo.inp file, otherwise CEA will throw an error.
%   inp('fuel_t'): Array of fuel temperatures (or a single one), matching
%       up with inp('fuel'). Must have the same number of elements as
%       inp('fuel').
%   inp('fuel_t_unit'): Fuel temperature unit. Can be 'K', 'C', 'R', or 'F'
%   inp('fuel_wt%'): Array of fuel weight percentages, matching up with
%       inp('fuel'). Optional if only one fuel is specified. Must have the
%       same number of elements as inp('fuel') otherwise.
%   inp('ox'): Array of ox names (or a single one). Each ox name must be
%       in the thermo.inp file, otherwise CEA will throw an error.
%   inp('ox_t'): Array of ox temperatures (or a single one), matching
%       up with inp('ox'). Must have the same number of elements as
%       inp('ox').
%   inp('ox_t_unit'): Ox temperature unit. Can be 'K', 'C', 'R', or 'F'
%   inp('ox_wt%'): Array of ox weight percentages, matching up with
%       inp('ox'). Optional if only one ox is specified. Must have the
%       same number of elements as inp('ox') otherwise.
%
% Notes:
%   Does not support string inputs. Surround all text with single quotes
%       instead of double quotes.
%   If you see a 'sqrt domain' error in the MATLAB stdout, that is a CEA
%       error. Your inputs are likely invalid given the thermo.inp and
%       trans.inp files being used. This error will still occur if you run
%       CEA manually.
%   Read more notes in 'cea_rocket_read.m'.
%
% Author: Phil Piper
% Maintainer: Phil Piper

% Developer TODO:
%   Test the limits of the maxes array. May be able to get some of them up
%       to 7 or 8, but thorough testing would be required.


%% Store caontainer Map so that the input isn't modified
inp_cpy = [inp; containers.Map()];


%% Insert an O/F of 0 if none is specified (monopropellant)
if ~isKey(inp_cpy, 'o/f') && ~isKey(inp_cpy, 'phi')
    if isKey(inp_cpy, 'fuel') && ~isempty(inp_cpy('fuel')) ...
            && isKey(inp_cpy, 'ox') && ~isempty(inp_cpy('ox'))
        fprintf('Bipropellant operation requires an O/F or phi\n');
    end
    inp_cpy('o/f') = 0;
end


%% Create an empty map if one isn't provided
if nargin < 2
    data = containers.Map();
end


%% Maximum number of each input
% From here on out indexing will be 1-p, 2-of, 3-ratio
maxes = [
    6,   % Chamber pressure
    6,   % O/F ratio
    6];  % Either pinf/p or area ratio


%% Gather the pressures, O/Fs, and ratios into a similar array
ratios = [];
is_subsup = true;
if isKey(inp_cpy, 'sub') && ~isempty(inp_cpy('sub'))
    % Differentiate subsonic from supersonic area ratios by making the
    % subsonic area ratios negative
    ratios = -1 * inp_cpy('sub');
end
if isKey(inp_cpy, 'sup') && ~isempty(inp_cpy('sup'))
    ratios = [ratios, inp_cpy('sup')];
end
if isKey(inp_cpy, 'pip') && ~isempty(inp_cpy('pip'))
    if ~isempty(ratios)
        error(['Either use pip or sup/sub, not both. Using' ...
            ' both is possible with CEA, but it makes data storage' ...
            ' in MATLAB messy.']);
    end
    is_subsup = false;
    ratios = inp_cpy('pip');
end

values = {
    inp_cpy('p'),
    inp_cpy('o/f'),
    ratios};


%% Preprocess some file name string manipulation
if isKey(inp_cpy, 'file_name') && ~isempty(inp_cpy('file_name'))
    file_name = inp_cpy('file_name');
    file_name_dots = find(file_name == '.');
    if isempty(file_name_dots)
        file_name_base = file_name;
        file_name_ext = '';
    else
        file_name_base = file_name(1:file_name_dots(end)-1);
        file_name_ext = file_name(file_name_dots(end):end);
    end
end


%% Split the problem up into multiple subproblems
split_values = {[], [], []};
for i = 1:length(maxes)
    if ~isempty(values{i})
        num_splits = ceil(length(values{i}) / maxes(i));
        splits = maxes(i) * ones(1, num_splits);
        splits(end) = length(values{i}) - (num_splits-1) * maxes(i);
        split_values{i} = mat2cell(values{i}, 1, splits);
    end
end


%% Run the subproblems, appending each solution to the data variable
ps = split_values{1};
ofs = split_values{2};
ratios = split_values{3};
no_ratios = false;
if isempty(ratios)
    % Account for the case where no ratios are given
    ratios(1) = 0;
    no_ratios = true;
end
m = 1; % Number of files generated (for naming purposes)
for i = 1:length(ps)
    for j = 1:length(ofs)
        for k = 1:length(ratios)
            % Print out the current progress
            fprintf('Running CEA call number %i of %i\n', m, ...
                length(ps)*length(ofs)*length(ratios));
            
            % Set the subproblem inputs
            inp_cpy('p') = ps{i};
            inp_cpy('o/f') = ofs{j};
            if no_ratios
                % Account for the case where no ratios are given
                inp_cpy('pip') = [];
                inp_cpy('sub') = [];
                inp_cpy('sup') = [];
            elseif is_subsup
                ratios_k = ratios{k};
                inp_cpy('pip') = [];
                inp_cpy('sub') = -1 * ratios_k(ratios_k < 0);
                inp_cpy('sup') = ratios_k(ratios_k > 0);
            else
                inp_cpy('pip') = ratios{k};
                inp_cpy('sub') = [];
                inp_cpy('sup') = [];
            end
            
            % Change the file_name if it is specified
            if isKey(inp_cpy, 'file_name') ...
                    && ~isempty(inp_cpy('file_name'))
                inp_cpy('file_name') = [file_name_base, num2str(m), ...
                    file_name_ext];
            end
            
            % Run the subproblem
            data = cea_rocket_run_single(inp_cpy, data);
            m = m + 1;
        end
    end
end

end