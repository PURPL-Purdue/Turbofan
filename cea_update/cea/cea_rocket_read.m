function [data] = cea_rocket_read(file_name, data)
%OUTREAD_ROCKET: Reads CEA rocket output files.
%
% Input
%   file_name: The name of the '.out' data file that CEA generates
%   data: 'cea_rocket_read' data file to append the results of processing
%       the contents of 'file_name' to. Only works if the reactants part of
%       the input file is the same between runs. Has a datatype of
%       containers.Map. This is an OPTIONAL variable.
%
% Output
%   data: Contains the contents of the output file
%   data(type): The type of CEA analysis; either 'eq' or 'fr'
%   data(type)('fuel*'): Various fuel properties including the fuel name,
%       temperature, weight percentage, and energy (for various *)
%   data(type)('ox*'): Various oxidizer properties including the oxidizer
%       name, temperature, weight percentage, and energy (for various *)
%   data(type)('pin'): Pressure list input to CEA
%   data(type)('o/f'): O/F list input to CEA
%   data(type)('pinf/p'): pinf/p list input to CEA
%   data(type)('ae/at'): ae/at list input to CEA
%   NOTE: Either the 'pinf/p' or 'ae/at' key will exist, not both. The
%       data(type)('ratio_type') key will tell you which one exists
%   data(type)(property): All of the properties output by CEA including
%       performance, thermal, and species (for equilibrium only) in a 3D
%       matrix. The three indices correspond to the input pin, o/f, and
%       whichever of pinf/p or ae/at was used in the input file, in that
%       order. The list of all of these properties can be obtained with
%       keys(data(type)).
%
% Notes
%   All properties are in SI units (kg, m, s, K).
%   Does not parse the throat values by default. A throat subsonic or
%       supersonic area ratio has to be specified explicitly.
%   As stated in the Output section, the molar concentrations are not
%       parsed for frozen flow. Ask the current maintainer to implement
%       this feature if you need it.
%   Does not verify that the same reactants are used when appending to a
%       given data file. Ask the current maintainer to implement this
%       feature if you need it.
%   Does not allow lower CEA trace values. Ask the current maintainer to
%       implement this feature if you need it.
%   The CEA equilibrium analysis also calculates frozen values for thermal
%       properties. These are different than the thermal properties
%       calculated by a CEA frozen analysis. These equilibrium frozen
%       thermal values are available in data('eq')('*_fr').
%   Reorders the pressure, mixture, and ratio inputs such that they are
%       sorted in ascending order.
%   Frozen flow does not work with a finite area combustor. This is a CEA
%       limitation.
%
% Author: Phil Piper
% Maintainer: Phil Piper

% Developer TODO:
%   Get rid of the fuel/ox arrays and replace with the same overwrite
%       method used everywhere else. This will clean up the map generating
%       code a bit.
%   Read the Notes above. There are multiple TODOs in there.
%   Identify when the user specifies phi instead of O/F by looking at the
%       part of the output file which is a repeat of the input file in
%       order to index the 3D arrays by phi instead of O/F. Or even better
%       yet, copy the phis, rs, and %fuels along with the O/F from map as
%       they are currently being left behind (shouldn't require
%       reindexing).
%   Could use some cleaning up, mainly by adding sensible code sections
%       with the double comment syntax %%.


% Create an empty map if one isn't provided
if nargin < 2
    data = containers.Map();
end

% Loop through every line of the file
fileID = fopen(file_name, 'r');
if fileID == -1, error('Can''t open file %s', file_name), end
line = strtrim(fgetl(fileID));
found_a_section = false;
ratio_type = '';
while ischar(line)
    line = strtrim(line);
    if startsWith(line, 'Pc/P')
        % Determine if pinf/p is the correct ratio_type
        if isstrprop(line(end), 'digit')
            if strcmp(ratio_type, 'ae/at')
                error('Conflicting ratio_type.');
            end
            ratio_type = 'pinf/p';
        end
    elseif startsWith2(line, 'SUPERSONIC') || startsWith2(line, 'SUBSONIC')
        % Determine if ae/at is the correct ratio_type
        if isstrprop(line(end), 'digit')
            if strcmp(ratio_type, 'pinf/p')
                error('Conflicting ratio_type.');
            end
            ratio_type = 'ae/at';
        end
    elseif startsWith2(line, 'THEORETICAL')
        % Beginning of a new section
        
        % If no ratio_type was set, then this is a chamber only
        % calculation. Use pinf/p as the ratio_type by default.
        if isempty(ratio_type)
            ratio_type = 'pinf/p';
        end
        
        % Instantiate the map and fuel/ox arrays
        found_a_section = true;
        map = containers.Map;
        fuel = {};
        fuel_wt = [];
        fuel_energy = [];
        fuel_T = [];
        ox = {};
        ox_wt = [];
        ox_energy = [];
        ox_T = [];
        
        % Determine if this section is for frozen or equilibrium flow
        if strfind(line, 'FROZEN')
            map('type') = 'fr';
        elseif strfind(line, 'EQUILIBRIUM')
            map('type') = 'eq';
        else
            assert(false);
        end
    elseif startsWith2(line, 'Pin =')
        % Get the chamber pressure
        pin_start = strfind(line, '=') + 1;
        pin_end = strfind(line(pin_start:end), 'P') + pin_start - 2;
        map('pin') = str2num(strtrim(line(pin_start:pin_end))) * 6894.76;
        if strfind(line(pin_start:pin_end), '*')
            error('ERROR: Your input pressure was way too high for CEA.');
        end
        assert(~isempty(map('pin')));
    elseif startsWith2(line, 'Ac/At =')
        % Get the finite area combustor ratio if applicable
        acat_start = strfind(line, '=') + 1;
        acat_start = acat_start(1);
        acat_end = strfind(line(acat_start:end), 'P') + acat_start - 2;
        acat_end = acat_end(1);
        map('ac/at') = str2num(strtrim(line(acat_start:acat_end)));
        if isempty(map('ac/at'))
            error('ERROR: Something went wrong with the Ac/At parsing.');
        end
        
        % Change the ratio_type to pinj/p if necessary
        if strcmp(ratio_type, 'pinf/p')
            ratio_type = 'pinj/p';
        end
    elseif startsWith2(line, 'MDOT/Ac =')
        % Get the finite area mass flowrate ratio if applicable
        mdot_start = strfind(line, '=') + 1;
        mdot_end = strfind(line(mdot_start:end), '(') + mdot_start - 2;
        map('mdot/ac') = str2num(strtrim(line(mdot_start:mdot_end)));
        if isempty(map('mdot/ac'))
            error('ERROR: Something went wrong with the mdot/Ac parsing.');
        end
        
        % Change the ratio_type to pinj/p if necessary
        if strcmp(ratio_type, 'pinf/p')
            ratio_type = 'pinj/p';
        end
    elseif startsWith2(line, 'FUEL')
        % Get the fuels
        fuel_index = size(fuel, 1) + 1;
        fuel_split = strsplit(strtrim(line(length('FUEL '):end)));
        fuel{fuel_index} = fuel_split{1};
        fuel_wt(fuel_index) = str2num(fuel_split{2});
        fuel_energy(fuel_index) = str2num(fuel_split{3}) * 1000;
        fuel_T(fuel_index) = str2num(fuel_split{4});
    elseif startsWith2(line, 'OXIDANT')
        % Get the oxidants
        ox_index = size(ox, 1) + 1;
        ox_split = strsplit(strtrim(line(length('OXIDANT '):end)));
        ox{ox_index} = ox_split{1};
        ox_wt(ox_index) = str2num(ox_split{2});
        ox_energy(ox_index) = str2num(ox_split{3}) * 1000;
        ox_T(ox_index) = str2num(ox_split{4});
    elseif startsWith2(line, 'O/F=')
        % Get the fuel/oxidizer ratio values
        ratios_split = strtrim(strsplit(line, {'=', ' '}));
        for i = 1:2:7
            key = cea_rocket_get_key_name(lower(ratios_split{i}));
            map(key) = str2num(ratios_split{i+1});
        end
    elseif startsWith2(line, 'CHAMBER') || startsWith2(line, 'INJECTOR')
        % Get all of the interesting values up until the mole fractions
        line = strtrim(fgetl(fileID));
        while (strcmp(map('type'), 'fr') ...
                && ~startsWith2(line, 'MOLE')) ...
                || (strcmp(map('type'), 'eq') ...
                && ~startsWith2(line, 'PRODUCTS'))
            % Go to the  next line if the key doesn't exist
            key_cutoff = 16;
            if length(line) < key_cutoff
                line = strtrim(fgetl(fileID));
                continue;
            end
            
            % Process the key into a better name
            key = line(1:key_cutoff);
            key = cea_rocket_get_key_name(key);
            
            % Rename the conductivity key so that it isn't as long.
            % Hopefully there isn't any elemental potassium in the exhaust.
            if strcmp(key, 'conductivity')
                key = 'k';
            end
            
            % If the key already exists and this is an equilibrium type,
            % then this is a frozen thermal value. Create a new key to not
            % overwrite the old one.
            if isKey(map, key)
                if strcmp(map('type'), 'fr')
                    line = strtrim(fgetl(fileID));
                    continue
                end
                key = [key, '_fr'];
            end
            
            % If the last character isn't a number, go to the next line
            if ~isstrprop(line(end), 'digit')
                line = strtrim(fgetl(fileID));
                continue
            end
            
            % Parse the values
%             vals = strsplit(strtrim(line(key_cutoff:end)));
            vals = strtrim(cellstr(reshape(line(key_cutoff:end), 9, ...
                [])'))';
            vals = vals(~cellfun(@isempty, vals));
            
            % Put the values into the map
            density_line = false;
            if strcmp(key, 'pinf/p') || strcmp(key, 'pinj/p')
                % Get the total number of expansion ratios
                vals_length = length(vals);
            elseif length(vals) < vals_length
                % Most of these keys are 0 at the chamber. Cstar is,
                % however, not 0 at the chamber; it is constant with ratio.
                if strcmp(key, 'cstar')
                    vals = [vals(1), vals];
                else
                    vals = ['0', vals];
                end
            elseif strcmp(key, 'rho')
                % Density requires some trickery due to its formatting
                vals = [];
                for i = 1:vals_length
                    start = key_cutoff + 9 * (i - 1);
                    val = strtrim(line(start:start+8));
                    if val(7) == ' '
                        val(7) = 'e';
                    elseif val(7) == '-'
                        val = [val(1:6), 'e', val(7:end)];
                    end
                    vals(i) = sscanf(val, '%f');
                    density_line = true;
                end
            else
                % Nothing to do for everything else
            end
            
            % Again, account for the density line being scientific notation
            if ~density_line
                vals = cellfun(@str2num, vals);
            end
            
            % Fix the units of various keys
            conversion = 1;
            if strcmp(key, 'p')
                conversion = 1e5;
            elseif strmatch(key, {'h', 'u', 'g', 's', 'cp'}, 'exact')
                conversion = 1e3;
            elseif strcmp(key, 'visc')
                conversion = 1e-4;
            elseif strcmp(key, 'k')
                conversion = 1e-1;
            end
            
            % If this is a finite area combustor, then do not record the
            % two default values (at Ac and throat) as opposed to just not
            % recording the throat for infinite area combustors.
            if isKey(map, 'ac/at') || isKey(map, 'mdot/ac')
                default_val_cutoff = 3;
            else
                default_val_cutoff = 2;
            end
            
            % Write the values to the map, without the default throat value
            if length(vals) > default_val_cutoff
                vals_end = vals(default_val_cutoff+1:end);
            else
                vals_end = [];
            end
            map(key) = conversion * [vals(1), vals_end];
            
            % Get a new trimmed line (assumes a new line exists)
            line = strtrim(fgetl(fileID));
        end
    elseif startsWith2(line, 'NOTE.')
        % End of a section
        map_append = containers.Map({'fuel', 'fuel_wt', 'fuel_energy', ...
            'fuel_t', 'ox', 'ox_wt', 'ox_energy', 'ox_t'}, {fuel, ...
            fuel_wt, fuel_energy, fuel_T, ox, ox_wt, ox_energy, ox_T});
        map = [map; map_append];
        
        % Create the type data map if it doesn't exist
        if ~isKey(data, map('type'))
            data(map('type')) = containers.Map();
        end
        
        % Insert or check the ratio_type
        data_type = data(map('type'));
        if ~isKey(data_type, ratio_type)
            data_type('ratio_type') = ratio_type;
        elseif ~strcmp(data_type('ratio_type'), ratio_type)
            error(['Output file ratio type of %s does not match file' ...
                ' ratio_type of %s'], data_type('ratio_type'), ratio_type);
        end
        
        % Insert or check fuel and ox information (and FAC)
        % TODO
        
        % Get the index of where pin should be placed
        new_pin_row = false;
        if ~isKey(data_type, 'pin')
            data_type('pin') = [];
        end
        pin_index = find(data_type('pin') < map('pin'));
        if isempty(pin_index)
            pin_index = 1;
        else
            pin_index = pin_index(end)+1;
        end
        data_type_pin = data_type('pin');
        if isempty(data_type_pin)
            data_type_pin = map('pin');
        elseif pin_index > length(data_type_pin) ...
                || data_type_pin(pin_index) ~= map('pin')
            data_type_pin = [data_type_pin(1:pin_index-1), ...
                map('pin'), data_type_pin(pin_index:end)];
            new_pin_row = true;
        end
        data_type('pin') = data_type_pin;
        
        % Get the index of where of should be placed
        new_of_row = false;
        if ~isKey(data_type, 'o/f')
            data_type('o/f') = [];
        end
        of_index = find(data_type('o/f') < map('o/f'));
        if isempty(of_index)
            of_index = 1;
        else
            of_index = of_index(end)+1;
        end
        data_type_of = data_type('o/f');
        if isempty(data_type_of)
            data_type_of = map('o/f');
        elseif of_index > length(data_type_of) ...
                || data_type_of(of_index) ~= map('o/f')
            data_type_of = [data_type_of(1:of_index-1), ...
                map('o/f'), data_type_of(of_index:end)];
            new_of_row = true;
        end
        data_type('o/f') = data_type_of;
        
        % Make the CR values negative to differentiate them from ER values
        if strcmp(ratio_type, 'ae/at')
            map(ratio_type) = map(ratio_type) .* ...
                ((map('mach') < 1) * -2 + 1);
        end
        
        % Adjust the ratio_type row with the new value
        if ~isKey(data_type, ratio_type)
            data_type(ratio_type) = map(ratio_type);
        else
            data_type(ratio_type) = [data_type(ratio_type), ...
                map(ratio_type)];
        end
        
        % Adjust and insert the new values into the data_type variable
        map_keys = union(keys(map), keys(data_type));
%         map_keys = keys(map);
        key_blacklist = {'fuel_wt', 'fuel_energy', 'fuel_t', 'ox_wt', ...
            'ox_energy', 'ox_t', 'pin', 'o/f', 'type', ratio_type, ...
            'ratio_type'};
        for i = 1:length(map_keys)
            key = map_keys{i};
            if ~isempty(strmatch(key, key_blacklist, 'exact'))
                % Skip blacklisted keys
                continue
            end
            if ~isKey(map, key)
                % data_type has the key but map does not. This can end up
                % happening with molar concentrations. Fix this by adding
                % an array of zeros according to the size of the
                % ratio_type.
                map(key) = zeros(1, length(map(ratio_type)));
            end
            if ~isvector(map(key)) || iscell(map(key)) ...
                    || length(map(key)) ~= length(map(ratio_type))
                if isnumeric(map(key))
                    map(key) = ones(1, length(map(ratio_type))) * map(key);
                else
                    continue;
                end
            end
            if ~isKey(data_type, key) && ~isKey(data_type, 'visc')
                % This key doesn't exist, so create the 3D matrix. 'visc'
                % is the last key, so only new keys for the first run go
                % here. If a molar concentration isn't in the first run,
                % but is in subsequent runs, it gets dealt with in the else
                % statement.
                vals3d = zeros(1, 1, length(map(ratio_type)));
                vals3d(1, 1, :) = map(key);
            else
                if ~isKey(data_type, key)
                    % Deal with molar concentration problems as explained
                    % in the if statement above. Note that MATLAB can't
                    % create a 1 x 1 x 1 3D array, it automatically
                    % squeezes it down to a 1 x 1 2D array. Therefore, we
                    % need some logic to account for MATLAB's shortcomings.
                    ref_size = size(data_type('visc'));
                    if length(ref_size) < 3
                        ref_size(3) = 1;
                    end
                    vals3d = zeros(ref_size(1), ref_size(2), ref_size(3));
                else
                    % Otherwise start vals3d as the old data
                    vals3d = data_type(key);
                end
                
                % Create the pin row if applicable
                if new_pin_row
                    vals3d_begin = vals3d(1:pin_index-1, :, :);
                    if isempty(vals3d_begin)
                        vals3d_begin = [];
                    end
                    vals3d_end = vals3d(pin_index:end, :, :);
                    if isempty(vals3d_end)
                        vals3d_end = [];
                    end
                    vals3d = cat(1, vals3d_begin, ...
                        zeros(1, size(vals3d, 2), size(vals3d, 3)), ...
                        vals3d_end);
                end
                
                % Create the O/F row if applicable
                if new_of_row
                    vals3d_begin = vals3d(:, 1:of_index-1, :);
                    if isempty(vals3d_begin)
                        vals3d_begin = [];
                    end
                    vals3d_end = vals3d(:, of_index:end, :);
                    if isempty(vals3d_end)
                        vals3d_end = [];
                    end
                    vals3d = cat(2, vals3d_begin, ...
                        zeros(size(vals3d, 1), 1, size(vals3d, 3)), ...
                        vals3d_end);
                end
                
                % Insert the ratio_type rows
                vals3d_original_size = size(vals3d, 3);
                vals3d = cat(3, vals3d, ...
                    zeros(size(vals3d, 1), size(vals3d, 2) ...
                    , length(map(ratio_type))));
                vals3d(pin_index, of_index, ...
                    vals3d_original_size+1:end) = map(key);
            end
            data_type(key) = vals3d;
        end
    elseif startsWith2(line, 'THAN 50 K')
        % Condensed species warning
        fprintf('WARNING: Condensed species at p = %f Pa, o/f = %f\n', ...
            map('pin'), map('o/f'));
    end
    
    % Get a new line without trimming just in case there is no line to get.
    % The new line will be trimmed at the top of the loop.
    line = fgetl(fileID);
end

if ~found_a_section
    % Notify the user if no sections were found
    error('No sections were found in "%s". Check your input file.', ...
        file_name);
end
    
% Delete duplicate ratio_type (abbreviated rt below) numbers
data_keys = keys(data);
for i = 1:length(data_keys)
    % Get the sort order and duplicate indices
    data_type = data(data_keys{i});
    rt = data_type('ratio_type');
    [rt_sorted, rt_order] = sort(data_type(rt));
    [rt_unique, rt_duplicates] = unique(rt_sorted, 'stable');
    
    % Move ae/at = 1 to the beginning of the sort order
    if strcmp(rt, 'ae/at')
        throat_index = find(rt_unique == 0);
        rt_unique = [rt_unique(throat_index), ...
            rt_unique(1:throat_index-1), rt_unique(throat_index+1:end)];
    end
    
    % Save the new ratio_type order
    data_type(rt) = rt_unique;

    % Iterate through every 3D matrix and reorder their final dimension
    data_type_keys = keys(data_type);
    for j = 1:length(data_type_keys)
        key = data_type_keys{j};

        % If this key's value isn't a 3D matrix, then skip it
        if length(size(data_type(key))) ~= 3
            continue;
        end
        
        % Add extra elements of 0 if vals3d isn't long enough to account
        % for elements they may have shown up in one equilibrium reaction,
        % but not another.
        vals3d = data_type(key);
        if size(vals3d, 3) < length(rt_order)
            vals3d = cat(3, vals3d, zeros(size(vals3d, 1), ...
                size(vals3d, 2), length(rt_order)-size(vals3d, 3)));
        end
        vals3d = vals3d(:, :, rt_order);

        % Remove the duplicates
        for k = flip(1:length(rt_duplicates))
            dup_start = rt_duplicates(k);
            if k < length(rt_duplicates)
                dup_end = rt_duplicates(k+1) - 1;
            else
                dup_end = size(vals3d, 3);
            end

            % There's probably a way to do this without the explicit loops
            for m = 1:size(vals3d, 1)
                for n = 1:size(vals3d, 2)
                    % All of the nonzero_vals should be the same since they
                    % have the same CEA inputs
                    nonzero_vals = ...
                        find(vals3d(m, n, dup_start:dup_end) ~= 0);
                    if isempty(nonzero_vals)
                        nonzero_vals = 1;
                    end
                    vals3d(m, n, dup_start) = ...
                        vals3d(m, n, dup_start+nonzero_vals(1)-1);
                end
            end

            % Delete the duplicate rows
            vals3d(:, :, dup_start+1:dup_end) = [];
        end
        
        % Move ae/at = 1 to the beginning of the sort order
        if strcmp(rt, 'ae/at')
            vals3d = cat(3, vals3d(:, :, throat_index), ...
                vals3d(:, :, 1:throat_index-1), ...
                vals3d(:, :, throat_index+1:end));
        end
        
        % Save the values
        data_type(key) = vals3d;
    end
end

% Close the file so it can be deleted if needed
fclose(fileID);

end