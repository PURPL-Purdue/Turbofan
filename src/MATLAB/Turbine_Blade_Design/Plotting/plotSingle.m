% Modifies the output matricies as required for aesthetics, then plots
function plotSingle(blade, type, plot_throat, plot_t_max, plot_bez_p1, LE_align, show_curvature, flip_stator, num_blades, profiles_to_plot, pitch_align, highlight)
    if highlight == "regular"
        lineStyle = '-k';
    elseif highlight == "highlight"
        lineStyle = '-b';
    end

    % Pitch calculation for multi-blade plotting
    pitch = blade(pitch_align).parameters.pitch;

    % Finding mirroring line
    y_flip = blade(pitch_align).parameters.Ct;

    if type == "stator" && flip_stator == true
        % Flipping Stator upside down a~nd translating back down
        for i = profiles_to_plot
            blade(i).y_comb          = 2*y_flip - blade(i).y_comb             - blade(pitch_align).parameters.Ct/2;
            blade(i).y_spline_pts    = 2*y_flip - blade(i).y_spline_pts       - blade(pitch_align).parameters.Ct/2;
            blade(i).y_suction       = 2*y_flip - blade(i).y_suction          - blade(pitch_align).parameters.Ct/2;
            blade(i).y               = 2*y_flip - blade(i).y                  - blade(pitch_align).parameters.Ct/2;
            blade(i).y_thicc         = 2*y_flip - blade(i).y_thicc            - blade(pitch_align).parameters.Ct/2;
            blade(i).y_o             = 2*y_flip - blade(i).y_o                - blade(pitch_align).parameters.Ct/2;
            blade(i).ps_p1y          = 2*y_flip - blade(i).ps_p1y             - blade(pitch_align).parameters.Ct/2;
            blade(i).norm_y = -blade(i).norm_y;
        end
    end

       % Lines up leading edges
    if LE_align
        for i = profiles_to_plot
            blade(i).y_comb          = blade(i).y_comb            - (blade(pitch_align).parameters.Ct-blade(i).parameters.Ct);
            blade(i).y_spline_pts    = blade(i).y_spline_pts      - (blade(pitch_align).parameters.Ct-blade(i).parameters.Ct);
            blade(i).y_suction       = blade(i).y_suction         - (blade(pitch_align).parameters.Ct-blade(i).parameters.Ct);
            blade(i).y               = blade(i).y                 - (blade(pitch_align).parameters.Ct-blade(i).parameters.Ct);
            blade(i).y_thicc         = blade(i).y_thicc           - (blade(pitch_align).parameters.Ct-blade(i).parameters.Ct);
            blade(i).y_o             = blade(i).y_o               - (blade(pitch_align).parameters.Ct-blade(i).parameters.Ct);
            blade(i).ps_p1y          = blade(i).ps_p1y            - (blade(pitch_align).parameters.Ct-blade(i).parameters.Ct);
        end
    end

    % Shifting upwards for multiple blade display
    % PLOTTING
    hold on
    [x_low, x_high, ~] = scale_graph(blade, pitch_align);
    min_ys = ones(1,length(profiles_to_plot)*(num_blades));
    max_ys = ones(1,length(profiles_to_plot)*(num_blades));

    % Plot the first blade
    counter = 1;
    for i = profiles_to_plot            
        plotProfile(blade(i), plot_throat, plot_t_max, plot_bez_p1, show_curvature, lineStyle)
        [min_ys(counter), max_ys(counter)] = maxmin_y(blade(i));
        counter = counter + 1;
    end

    % Plot additional blades
    for j = 1:num_blades-1
        for i = profiles_to_plot
            blade(i).y_comb          = blade(i).y_comb        + pitch;
            blade(i).y_spline_pts    = blade(i).y_spline_pts  + pitch;
            blade(i).y_suction       = blade(i).y_suction     + pitch;
            blade(i).y               = blade(i).y             + pitch;
            blade(i).y_thicc         = blade(i).y_thicc       + pitch;
            blade(i).y_o             = blade(i).y_o           + pitch;
            blade(i).ps_p1y          = blade(i).ps_p1y        + pitch;

            plotProfile(blade(i), plot_throat, plot_t_max, plot_bez_p1, show_curvature, lineStyle)
            [min_ys(counter), max_ys(counter)] = maxmin_y(blade(i));
            counter = counter + 1;
        end
    end
    
    y_extension = 8;
    y_low = min(min_ys)-y_extension;
    y_high = max(max_ys)+y_extension;

    xlim([x_low,x_high]);
    ylim([y_low,y_high]);
    pbaspect([x_high-x_low,y_high-y_low,blade(pitch_align).parameters.blade_height]);
    
end

% Autoscales the plot
function [x_low, x_high, y_diff] = scale_graph(blade, pitch_align)
    x_low = min(blade(pitch_align).x_comb) - 2;
    x_high = max(blade(pitch_align).x_comb) + 2;
    y_low = min(blade(pitch_align).y_comb);
    y_high = max(blade(pitch_align).y_comb);
    y_diff = y_high - y_low;
end

function [y_low, y_high] = maxmin_y(blade)
    y_low = min(blade.y_comb);
    y_high = max(blade.y_comb);
end