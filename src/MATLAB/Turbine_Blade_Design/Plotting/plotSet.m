% Modifies the output matricies as required for aesthetics, then plots
function plotSet(rotor_blade, stator_blade, plot_throat, plot_t_max, plot_bez_p1, LE_align, show_curvature, flip_stator, num_stator, num_rotor, profiles_to_plot, pitch_align)
    % Pitch calculation for multi-blade plotting
    stator_pitch = stator_blade(pitch_align).parameters.pitch;
    rotor_pitch = rotor_blade(pitch_align).parameters.pitch;

    % Finding mirroring line
    y_flip = (rotor_blade(pitch_align).parameters.Ct + stator_blade(pitch_align).parameters.Ct)/2;
    % Calculating x-offset for rotor plotting
    x_offset = 1.2*stator_blade(pitch_align).parameters.Cx;
    
    % Prepping the blades (flipping stator, aligning LEs)
    % Flipping Stator upside down and translating back down
    if flip_stator
        for i = profiles_to_plot
            stator_blade(i).y_comb          = 2*y_flip - stator_blade(i).y_comb             - stator_blade(pitch_align).parameters.Ct/2;
            stator_blade(i).y_spline_pts    = 2*y_flip - stator_blade(i).y_spline_pts       - stator_blade(pitch_align).parameters.Ct/2;
            stator_blade(i).y_suction       = 2*y_flip - stator_blade(i).y_suction          - stator_blade(pitch_align).parameters.Ct/2;
            stator_blade(i).y               = 2*y_flip - stator_blade(i).y                  - stator_blade(pitch_align).parameters.Ct/2;
            stator_blade(i).y_thicc         = 2*y_flip - stator_blade(i).y_thicc            - stator_blade(pitch_align).parameters.Ct/2;
            stator_blade(i).y_o             = 2*y_flip - stator_blade(i).y_o                - stator_blade(pitch_align).parameters.Ct/2;
            stator_blade(i).ps_p1y          = 2*y_flip - stator_blade(i).ps_p1y             - stator_blade(pitch_align).parameters.Ct/2;
            stator_blade(i).norm_y = -stator_blade(i).norm_y;
        end
    end
    
    % Lines up leading edges
    if LE_align
        for i = profiles_to_plot
            stator_blade(i).y_comb          = stator_blade(i).y_comb            - (stator_blade(pitch_align).parameters.Ct-stator_blade(i).parameters.Ct);
            stator_blade(i).y_spline_pts    = stator_blade(i).y_spline_pts      - (stator_blade(pitch_align).parameters.Ct-stator_blade(i).parameters.Ct);
            stator_blade(i).y_suction       = stator_blade(i).y_suction         - (stator_blade(pitch_align).parameters.Ct-stator_blade(i).parameters.Ct);
            stator_blade(i).y               = stator_blade(i).y                 - (stator_blade(pitch_align).parameters.Ct-stator_blade(i).parameters.Ct);
            stator_blade(i).y_thicc         = stator_blade(i).y_thicc           - (stator_blade(pitch_align).parameters.Ct-stator_blade(i).parameters.Ct);
            stator_blade(i).y_o             = stator_blade(i).y_o               - (stator_blade(pitch_align).parameters.Ct-stator_blade(i).parameters.Ct);
            stator_blade(i).ps_p1y          = stator_blade(i).ps_p1y            - (stator_blade(pitch_align).parameters.Ct-stator_blade(i).parameters.Ct);

            rotor_blade(i).y_comb           = rotor_blade(i).y_comb             + (rotor_blade(pitch_align).parameters.Ct-rotor_blade(i).parameters.Ct);
            rotor_blade(i).y_spline_pts     = rotor_blade(i).y_spline_pts       + (rotor_blade(pitch_align).parameters.Ct-rotor_blade(i).parameters.Ct);
            rotor_blade(i).y_suction        = rotor_blade(i).y_suction          + (rotor_blade(pitch_align).parameters.Ct-rotor_blade(i).parameters.Ct);
            rotor_blade(i).y                = rotor_blade(i).y                  + (rotor_blade(pitch_align).parameters.Ct-rotor_blade(i).parameters.Ct);
            rotor_blade(i).y_thicc          = rotor_blade(i).y_thicc            + (rotor_blade(pitch_align).parameters.Ct-rotor_blade(i).parameters.Ct);
            rotor_blade(i).y_o              = rotor_blade(i).y_o                + (rotor_blade(pitch_align).parameters.Ct-rotor_blade(i).parameters.Ct);
            rotor_blade(i).ps_p1y           = rotor_blade(i).ps_p1y             + (rotor_blade(pitch_align).parameters.Ct-rotor_blade(i).parameters.Ct);
        end
    end

    % Shifting rotor to the right
    for i = profiles_to_plot
        rotor_blade(i).x_comb           = rotor_blade(i).x_comb             + x_offset;
        rotor_blade(i).x_spline_pts     = rotor_blade(i).x_spline_pts       + x_offset;
        rotor_blade(i).x_suction        = rotor_blade(i).x_suction          + x_offset;
        rotor_blade(i).x                = rotor_blade(i).x                  + x_offset;
        rotor_blade(i).x_o              = rotor_blade(i).x_o                + x_offset;
        rotor_blade(i).x_thicc          = rotor_blade(i).x_thicc            + x_offset;
        rotor_blade(i).ps_p1x           = rotor_blade(i).ps_p1x             + x_offset;
    end

    % Shifting upwards for multiple blade display
    % PLOTTING
    hold on
    [x_low, x_high, ~] = scale_graph(stator_blade, rotor_blade);
    min_ys = ones(1,length(profiles_to_plot)*(num_stator+num_stator));
    max_ys = ones(1,length(profiles_to_plot)*(num_stator+num_stator));

    % Plot the first blade
    counter = 1;
    for i = profiles_to_plot            
        plotProfile(stator_blade(i), plot_throat, plot_t_max, plot_bez_p1, show_curvature, '-k')
        [min_ys(counter), max_ys(counter)] = maxmin_y(stator_blade(i));
        counter = counter + 1;
        plotProfile(rotor_blade(i), plot_throat, plot_t_max, plot_bez_p1, show_curvature, '-k')
        [min_ys(counter), max_ys(counter)] = maxmin_y(rotor_blade(i));
        counter = counter + 1;
    end

    % Plot additional blades
    for j = 1:num_stator-1
        for i = profiles_to_plot
            stator_blade(i).y_comb          = stator_blade(i).y_comb        + stator_pitch;
            stator_blade(i).y_spline_pts    = stator_blade(i).y_spline_pts  + stator_pitch;
            stator_blade(i).y_suction       = stator_blade(i).y_suction     + stator_pitch;
            stator_blade(i).y               = stator_blade(i).y             + stator_pitch;
            stator_blade(i).y_thicc         = stator_blade(i).y_thicc       + stator_pitch;
            stator_blade(i).y_o             = stator_blade(i).y_o           + stator_pitch;
            stator_blade(i).ps_p1y          = stator_blade(i).ps_p1y        + stator_pitch;

            plotProfile(stator_blade(i), plot_throat, plot_t_max, plot_bez_p1, show_curvature, '-k')
            [min_ys(counter), max_ys(counter)] = maxmin_y(stator_blade(i));
            counter = counter + 1;
        end
    end
    for j = 1:num_rotor-1
        for i = profiles_to_plot
            rotor_blade(i).y_comb           = rotor_blade(i).y_comb             + rotor_pitch;
            rotor_blade(i).y_spline_pts     = rotor_blade(i).y_spline_pts       + rotor_pitch;
            rotor_blade(i).y_suction        = rotor_blade(i).y_suction          + rotor_pitch;
            rotor_blade(i).y                = rotor_blade(i).y                  + rotor_pitch;
            rotor_blade(i).y_thicc          = rotor_blade(i).y_thicc            + rotor_pitch;
            rotor_blade(i).y_o              = rotor_blade(i).y_o                + rotor_pitch;
            rotor_blade(i).ps_p1y           = rotor_blade(i).ps_p1y             + rotor_pitch;

            plotProfile(rotor_blade(i), plot_throat, plot_t_max, plot_bez_p1, show_curvature, '-k')
            [min_ys(counter), max_ys(counter)] = maxmin_y(rotor_blade(i));
            counter = counter + 1;
        end
    end

    y_extension = 8;
    y_low = min(min_ys)-y_extension;
    y_high = max(max_ys)+y_extension;

    xlim([x_low,x_high]);
    ylim([y_low,y_high]);
    pbaspect([x_high-x_low,y_high-y_low,stator_blade(pitch_align).parameters.blade_height]);
    
end

% Autoscales the plot
function [x_low, x_high, y_diff] = scale_graph(stator_blade, rotor_blade)
    x_low = min([stator_blade(1:length(stator_blade)).x_comb]) - 2;
    x_high = max([rotor_blade(1:length(rotor_blade)).x_comb]) + 2;
    y_total_stator = stator_blade(1:length(stator_blade)).y_comb;
    y_total_rotor = rotor_blade(1:length(rotor_blade)).y_comb;
    y_total = [y_total_stator, y_total_rotor];
    y_low = min(y_total);
    y_high = max(y_total);
    y_diff = y_high - y_low;
end

function [y_low, y_high] = maxmin_y(blade)
    y_low = min(blade.y_comb);
    y_high = max(blade.y_comb);
end