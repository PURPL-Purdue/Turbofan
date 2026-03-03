% Modifies the output matricies as required, then exports
function export(rotor_blade, stator_blade, LE_align, pitch_align, mid_index)
    % Pitch calculation for multi-blade plotting
    stator_pitch = stator_blade(pitch_align).parameters.pitch;
    rotor_pitch = rotor_blade(pitch_align).parameters.pitch;

    % Finding the mid profile

    % Finding mirroring line
    y_flip = (rotor_blade(mid_index).parameters.Ct + stator_blade(mid_index).parameters.Ct)/2;
    % Calculating x-offset for rotor plotting
    x_offset = 1.2*stator_blade(mid_index).parameters.Cx;
    
    %% Prepping the blades (flipping stator, aligning LEs)
    [rotor_blade, stator_blade] = prep_setPlot(rotor_blade, stator_blade, LE_align, y_flip, mid_index);

    % Must export at this stage to capture only flipped stator geometry
        export_solidworks(stator_blade, "stator" , "", x_offset, mid_index)
        export_solidworks(rotor_blade, "rotor" , "", x_offset, mid_index)

    % Shifting upwards for additional blades
    for j = 1:2
        stator_blade(mid_index).y_comb = stator_blade(mid_index).y_comb + stator_pitch;
        if j == 1
            export_solidworks(stator_blade, "stator", "_shifted", x_offset, mid_index)
        elseif j == 2
            export_solidworks(stator_blade, "stator", "_shifted_twice", x_offset, mid_index)
        end
    end
    for j = 1:3
        rotor_blade(mid_index).y_comb = rotor_blade(mid_index).y_comb + rotor_pitch;
        if j == 1
            export_solidworks(rotor_blade, "rotor", "_shifted", x_offset, mid_index)
        elseif j == 2
            export_solidworks(rotor_blade, "rotor", "_shifted_twice", x_offset, mid_index)
        end
    end
end

% Preps the XY matrix and makes it a format that Solidworks likes
function xyz = export_prep(blade, R, Ct)
    z = ones(1,length(blade.x_comb))*R;
    y = blade.y_comb-Ct/2;
    xyz = [blade.x_comb', y', z'];
    i = 1;
    while i < length(xyz)
        if xyz(i,:) == xyz(i+1,:)
            xyz(i+1,:) = [];
        elseif norm(xyz(i+1,:)-xyz(i,:)) < 0.01
            xyz(i+1,:) = [];
        else
            i = i+1;
        end
    end
    if xyz(end, :) ~= xyz(1,:)
        xyz = [xyz; xyz(1,:)];
    end
end

% Writes the prepped final XY matricies to .txt files
function export_solidworks(blade, name, addon, x_offset, mid_index)
    % EXPORTING
    folder = fileparts(fileparts(mfilename('fullpath'))); 

    if name == "rotor" && (addon == "_shifted" || addon == "_shifted_twice")
        for i = [1, 2, mid_index, length(blade)-1, length(blade)]
            blade(i).x_comb  = blade(i).x_comb  - x_offset;
        end
    end

    writematrix(export_prep(blade(1), blade(1).parameters.R, blade(1).parameters.Ct), fullfile(folder, "Curve_Files\" + name + "_hub_extension" + addon + ".txt"), 'Delimiter', 'tab');
    writematrix(export_prep(blade(2), blade(2).parameters.R, blade(2).parameters.Ct), fullfile(folder, "Curve_Files\" + name + "_hub" + addon + ".txt"), 'Delimiter', 'tab');
    writematrix(export_prep(blade(mid_index),       blade(mid_index).parameters.R,          blade(mid_index).parameters.Ct),        fullfile(folder, "Curve_Files\" + name + "_mid" + addon + ".txt"), 'Delimiter', 'tab');
    writematrix(export_prep(blade(length(blade)-1), blade(length(blade)-1).parameters.R,    blade(length(blade)-1).parameters.Ct),  fullfile(folder, "Curve_Files\" + name + "_tip" + addon + ".txt"), 'Delimiter', 'tab');
    writematrix(export_prep(blade(length(blade)),   blade(length(blade)).parameters.R,      blade(length(blade)).parameters.Ct),    fullfile(folder, "Curve_Files\" + name + "_tip_extension" + addon + ".txt"), 'Delimiter', 'tab');
end

function [rotor_blade, stator_blade] = prep_setPlot(rotor_blade, stator_blade, LE_align, y_flip, mid_index)
    % Flipping Stator upside down and translating back down
    for i = [1, 2, mid_index, length(rotor_blade)-1, length(rotor_blade)]
        stator_blade(i).y_comb = 2*y_flip - stator_blade(i).y_comb - stator_blade(2).parameters.Ct/2;
    end
    
    % Lines up leading edges
    if LE_align
        for i = [1, 2, mid_index, length(rotor_blade)-1, length(rotor_blade)]
            stator_blade(i).y_comb = stator_blade(i).y_comb - (stator_blade(2).parameters.Ct-stator_blade(i).parameters.Ct);
            rotor_blade(i).y_comb  = rotor_blade(i).y_comb  + (rotor_blade(2).parameters.Ct-rotor_blade(i).parameters.Ct);
        end
    end
end