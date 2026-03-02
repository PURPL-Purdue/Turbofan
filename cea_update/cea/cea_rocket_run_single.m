function [data] = cea_rocket_run_single(inp, data)
%CEA_ROCKET_RUN_SINGLE CEA wrapper that does not account for CEAs input
%   limitations for pressure, mixture, and ratio.
%
% Input (General)
%   inp: A containers.Map datatype containing the CEA input parameters.
%   data: A containers.Map that returns the CEA output data. See the
%       'cea_rocket_read.m' help string for details.
%   inp('file_name'): The file name used for the generated input and output
%       files. If not specified, a random file name will be used and the
%       input/output files will be deleted after use. If a file name is
%       specified with this parameter, the input/output files will not be
%       deleted.
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
%   Don't use this file, except for debugging purposes or to
%       programmatically generate a good looking input file.
%       'cea_rocket_run.m' does the same thing as this file except it isn't
%       held back by CEA's pressure, mixture, and ratio limiations.
%   Read more notes in 'cea_rocket_read.m'.
%
% Author: Phil Piper
% Maintainer: Phil Piper

% Developer TODO:
%   Create an input flag that prevents this function from running CEA, thus
%       only generating an input file. In the same manner of thinking,
%       create a flag that generates the input file and runs CEA, but does
%       not read the output file.
%   Create inputs for fuel and oxidizer energies. Make sure the input is in
%       SI units (J/kg/K) to match up with 'cea_rocket_read.m' standards.
%   Make the UNIX run section similar to the Windows one such that the cea/
%       directory can be installed on a system via MATLAB's pathing.
%   Create an input flag for suppressing warnings.
%   Change the type input such that it is true/false for eq/fr. Also add an
%       option for setting the freeze point.


%% Create an empty map if one isn't provided
if nargin < 2
    data = containers.Map();
end


%% Open the input file
if isKey(inp, 'file_name') && ~isempty(inp('file_name'))
    % Insure that the file extension is '.inp'
    file_name = inp('file_name');
    if length(file_name) < 4 ...
            || ~strcmp(file_name(length(file_name)-3:end), '.inp')
        file_name = strcat(file_name, '.inp');
    end
    % If the file_name is specified, keep the input file after running
    keep_file = true;
else
    % Generate a random file name from the alphabet with a given length
    chars = char('a':'z');
    file_name_length = 20;
    file_name = chars(ceil(length(chars) * rand(1, file_name_length)));
    file_name = strcat(file_name, '.inp');
    % Remove the randomly generated input file after running
    keep_file = false;
end
fileID = fopen(file_name, 'w+');


%% Print the problem type for specifying equilibrium, frozen, ions, etc.
fprintf(fileID, 'problem rocket');
if isKey(inp, 'type') && ~isempty(inp('type'))
    fprintf(fileID, ' %s', inp('type'));
end
fprintf(fileID, '\n');


%% Finite area combustor settings
fac_set = false;
if isKey(inp, 'mdot') && ~isempty(inp('mdot'))
    fprintf(fileID, '    fac mdot = %.4f\n', inp('mdot'));
    fac_set = true;
end
if isKey(inp, 'ac') && ~isempty(inp('ac'))
    if fac_set
        fclose(fileID);
        delete(file_name);
        error('Chamber pressure p isn''t set');
    end
    fprintf(fileID, '    fac ac = %.4f\n', inp('ac'));
end


%% Print the chamber pressure
% Check that a chamber pressure was given
if ~isKey(inp, 'p') || isempty(inp('p'))
    fclose(fileID);
    delete(file_name);
    error('Chamber pressure p isn''t set');
end

% Get the chamber pressure unit
p_unit = 'bar';
if isKey(inp, 'p_unit')
    p_unit = inp('p_unit');
end

% Print the chamber pressure with unit
fprintf(fileID, '    p(%s) = %s\n', p_unit, ...
    strjoin(strtrim(cellstr(num2str(inp('p')'))'), ', '));


%% Print the mixture ratios and equivalence ratios
ratio_set = false;
if isKey(inp, 'o/f') && ~isempty(inp('o/f'))
    fprintf(fileID, '    o/f = %s\n', ...
        strjoin(strtrim(cellstr(num2str(inp('o/f')'))'), ', '));
    ratio_set = true;
end
if isKey(inp, 'phi') && ~isempty(inp('phi'))
    % Only use o/f if both o/f and phi are specified
    if ratio_set
        fprintf(strcat('WARNING: Both o/f and phi specified.', ...
            ' Only o/f will be used.'));
    else
        fprintf(fileID, '    phi = %s\n', ...
            strjoin(strtrim(cellstr(num2str(inp('phi')'))'), ', '));
        ratio_set = true;
    end
end

% Print a warning if neither o/f or phi are set
if ~ratio_set
    fprintf(strcat('WARNING: Neither o/f nor phi are set.', ...
        ' This better be a monopropellant rocket.\n'));
end


%% Print the pressure ratios, expansion ratios, and contraction ratios
ratio_set = false;
ratio_pip = false;
if isKey(inp, 'pip') && ~isempty(inp('pip'))
    fprintf(fileID, '    pip = %s\n', ...
        strjoin(strtrim(cellstr(num2str(inp('pip')'))'), ', '));
    ratio_set = true;
    ratio_pip = true;
end
if isKey(inp, 'sup') && ~isempty(inp('sup'))
    if ratio_pip
        fclose(fileID);
        delete(file_name);
        error(['Either use pip or sup/sub, not both. Using' ...
            ' both is possible with CEA, but it makes data storage' ...
            ' in MATLAB messy.']);
    end
    fprintf(fileID, '    sup = %s\n', ...
        strjoin(strtrim(cellstr(num2str(inp('sup')'))'), ', '));
    ratio_set = true;
end
if isKey(inp, 'sub') && ~isempty(inp('sub'))
    fprintf(fileID, '    sub = %s\n', ...
        strjoin(strtrim(cellstr(num2str(inp('sub')'))'), ', '));
    ratio_set = true;
end

% Print a warning if pip, sup, and sub aren't set
if ~ratio_set
    fprintf(strcat('WARNING: None of pip, sub, or sup were set.', ...
        ' The only outputs reported will be for the chamber.\n'));
end


%% Print the fuels
fprintf(fileID, 'reac\n');
fuel_set = false;
% Get the fuel temperature unit
fuel_t_unit = 'K';
if isKey(inp, 'fuel_t_unit')
    fuel_t_unit = inp('fuel_t_unit');
end

% Check the fuel arrays then print the fuels
if isKey(inp, 'fuel')
    % Get the fuel input and make sure it is a cell array
    fuel = inp('fuel');
    if ischar(fuel)
        fuel = {fuel};
    end
    if isKey(inp, 'fuel_t')
        fuel_t = inp('fuel_t');
        % Make sure the number of fuel temperatures match the number of
        % fuels
        if length(fuel) ~= length(fuel_t)
            fclose(fileID);
            delete(file_name);
            error(strcat('Number of fuels and number of', ...
                ' fuel temperatures do not match.'));
        end
    end
    if isKey(inp, 'fuel_wt%')
        fuel_wt = inp('fuel_wt%');
        % Make sure the number of fuel weight percentages match the number
        % of fuels
        if length(fuel) ~= length(fuel_wt)
            fclose(fileID);
            delete(file_name);
            error(strcat('Number of fuels and number of', ...
                ' fuel weight percentages do not match.'));
        end
    elseif iscell(inp('fuel')) && length(inp('fuel')) > 1
        fclose(fileID);
        delete(file_name);
        error(strcat('Number of fuels and number of', ...
            ' fuel weight percentages do not match.'));
    end
    
    % Print the fuels
    for i = 1:length(fuel)
        fprintf(fileID, '    fuel = %s', fuel{i});
        if isKey(inp, 'fuel_t')
            fprintf(fileID, ' t(%s) = %.3f', fuel_t_unit, fuel_t(i));
        end
        if isKey(inp, 'fuel_wt%')
            fprintf(fileID, ' wt%% = %.3f', fuel_wt(i));
        end
        fprintf(fileID, '\n');
    end
    fuel_set = true;
else
    fprintf(strcat('WARNING: No fuel specified.', ...
        ' This better be a monopropellant rocket.\n'));
end


%% Print oxidizers (literally a copy and paste of the fuels bit above)
% Get the ox temperature unit
ox_t_unit = 'K';
if isKey(inp, 'ox_t_unit')
    ox_t_unit = inp('ox_t_unit');
end

% Check the ox arrays then print the oxs
if isKey(inp, 'ox')
    % Get the ox input and make sure it is a cell array
    ox = inp('ox');
    if ischar(ox)
        ox = {ox};
    end
    if isKey(inp, 'ox_t')
        ox_t = inp('ox_t');
        % Make sure the number of ox temperatures match the number of oxs
        if length(ox) ~= length(ox_t)
            fclose(fileID);
            delete(file_name);
            error(strcat('Number of oxs and number of ', ...
                'ox temperatures do not match.'));
        end
    end
    if isKey(inp, 'ox_wt%')
        ox_wt = inp('ox_wt%');
        % Make sure the number of ox weight percentages match the number
        % of oxs
        if length(ox) ~= length(ox_wt)
            fclose(fileID);
            delete(file_name);
            error(strcat('Number of oxs and number of', ...
                ' ox weight percentages do not match.'));
        end
    elseif iscell(inp('ox')) && length(inp('ox')) > 1
        fclose(fileID);
        delete(file_name);
        error(strcat('Number of oxs and number of', ...
            ' ox weight percentages do not match.'));
    end
    
    % Print the oxs
    for i = 1:length(ox)
        fprintf(fileID, '    ox = %s', ox{i});
        if isKey(inp, 'ox_t')
            fprintf(fileID, ' t(%s) = %.3f', ox_t_unit, ox_t(i));
        end
        if isKey(inp, 'ox_wt%')
            fprintf(fileID, ' wt%% = %.3f', ox_wt(i));
        end
        fprintf(fileID, '\n');
    end
else
    if fuel_set
        fprintf(strcat('WARNING: No ox specified.', ...
            ' This better be a monopropellant rocket.\n'));
    else
        fclose(fileID);
        delete(file_name);
        error('No fuel or ox specified.');
    end
end


%% Omit species setting
if isKey(inp, 'omit') && ~isempty(inp('omit'))
    if iscell(inp('omit'))
        omit_str = strjoin(inp('omit'), ' ');
    else
        omit_str = inp('omit');
    end
    fprintf(fileID, 'omit %s\n', omit_str);
end


%% Print output related stuff
fprintf(fileID, 'outp trans\nend\n');


%% Write the input file
fclose(fileID);


%% Run the input file and redirect their stdout to NULL for cleanliness
cea_location = fileparts(which(mfilename()));
file_name_base = file_name(1:length(file_name)-4);
cea_output_file = [cea_location '\' file_name_base '.out'];
cea_input_file = [cea_location '\' file_name];
if ispc()
    % Copy the input file to the CEA directory and run CEA. This will pop
    % open a command prompt window which will close. It has to be this way
    % in order to change the directory for FCEA2.exe to operate properly.
    if ~strcmp(pwd(), cea_location)
        copyfile(file_name, [cea_location '\' file_name]);
    end
    system(sprintf('START /min /D "%s" cmd /c "echo %s | FCEA2.exe"', ...
        fileparts(which(mfilename())), file_name_base));
    
    % Wait until the output file exists
    while exist(cea_output_file, 'file') ~= 2
        pause(0.1);
    end
    
    % Wait until FCEA2.exe is done with the output file
    temp = fopen(cea_output_file, 'a+');
    while temp == -1
        pause(0.01);
        temp = fopen(cea_output_file, 'a+');
    end
    fclose(temp);
    
    % Move the output file to the current directory for further operations.
    if ~strcmp(pwd(), cea_location)
        movefile(cea_output_file, [file_name_base '.out']);
    end
elseif isunix()
    % TODO: Something similar to the Windows setup for installation
    system(sprintf('echo %s > ./FCEA2 > /dev/null', ...
        file_name(1:length(file_name)-4)));
end

%% Read the output file and return the data
file_name_out = [file_name(1:length(file_name)-4), '.out'];
pause(1); % Guarantee that CEA is done writing before reading data
data = cea_rocket_read(file_name_out, data);


%% Delete the input and output files if their names were randomly generated
if ~keep_file
    delete(file_name);
    
    % Wait until the output file exists
    while exist(file_name_out, 'file') ~= 2
        pause(0.01);
    end
    delete(file_name_out);
end

%% Delete the input file actually used no matter what
if exist(cea_input_file, 'file') == 2
    %delete(cea_input_file);
end

end