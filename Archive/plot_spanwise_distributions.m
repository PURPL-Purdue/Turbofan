function plot_spanwise_distributions(num_stages, num_stations, chord_m, r_mean_1, r_hub_vec, r_tip_vec, FF)
    figure(2); clf;
    tiledlayout(3,1, TileSpacing='tight', Padding='tight')

    %% Degree of Reaction
    nexttile
    hold on
    title("Degree of Reaction")
    [x_axis, ~] = plot_annulus(num_stages, chord_m, r_mean_1, r_hub_vec, r_tip_vec, FF);
    
    % Degree of Reaction
    for i = 1:num_stages
        scatter(x_axis(i)*ones(1, FF.num_streamlines), FF.r_spans{i*2-1}, [], FF.degR_spans{i})
    end
    colormap("turbo")
    colorbar
    
    ylim([0,max(r_tip_vec)*1.2])
    xlim([x_axis(1), x_axis(end)])
    pbaspect([range(x_axis),max(r_tip_vec)*1.2,1])
    grid minor
    xlabel("z (m)")
    ylabel("r (m)")
    
    nexttile
    hold on
    title("C_{\theta} Velocity")
    [x_axis, x_axis_long] = plot_annulus(num_stages, chord_m, r_mean_1, r_hub_vec, r_tip_vec, FF);
    
    % Ctheta Spanwise Distributions
    for i = 1:num_stations
        scatter(x_axis_long(i)*ones(1, FF.num_streamlines), FF.r_spans{i}, [], FF.Ctheta_spans{i})
    
        Ctheta_max = max(FF.Ctheta_spans{i});
        branches = FF.Ctheta_spans{i} / Ctheta_max * (0.9*chord_m);
        trunk = linspace(0.25*r_hub_vec(1), 0.75*r_hub_vec(1), FF.num_streamlines);
    
        if mod(i, 2) == 0
            style = '-w';
        else
            style = '-b';
        end
        plot_tree(trunk, branches, x_axis_long(i), 0, 0, style)
    end
    colormap("turbo")
    colorbar
    
    ylim([0,max(r_tip_vec)*1.2])
    xlim([x_axis(1), x_axis(end)])
    pbaspect([range(x_axis),max(r_tip_vec)*1.2,1])
    grid minor
    xlabel("z (m)")
    ylabel("r (m)")
    
    nexttile
    hold on
    title("C_z Velocity")
    [x_axis, x_axis_long] = plot_annulus(num_stages, chord_m, r_mean_1, r_hub_vec, r_tip_vec, FF);
    
    for i = 1:num_stations
        scatter(x_axis_long(i)*ones(1, FF.num_streamlines), FF.r_spans{i}, [], FF.z_spans{i})
    
        z_max = max(FF.z_spans{i});
        branches = FF.z_spans{i} / z_max * (0.9*chord_m);
        trunk = linspace(0.25*r_hub_vec(1), 0.75*r_hub_vec(1), FF.num_streamlines);
    
        if mod(i, 2) == 0
            style = '-w';
        else
            style = '-b';
        end
        plot_tree(trunk, branches, x_axis_long(i), 0, 0, style)
    end
    colormap("turbo")
    colorbar
    
    ylim([0,max(r_tip_vec)*1.2])
    xlim([x_axis(1), x_axis(end)])
    pbaspect([range(x_axis),max(r_tip_vec)*1.2,1])
    grid minor
    xlabel("z (m)")
    ylabel("r (m)")


    function [x_axis, x_axis_long] = plot_annulus(num_stages, chord_m, r_mean_1, r_hub_vec, r_tip_vec, FF)
        x_axis = 1:1:num_stages+1;
        x_axis = (x_axis-1) * 2 * chord_m;
        yline(r_mean_1)
        plot(x_axis, [r_hub_vec', r_tip_vec'], '.-r')
        x_axis_long = 1:1:FF.num_stations;
        x_axis_long = (x_axis_long-1) * chord_m;
        plot(x_axis_long, [FF.r_hub_vec_full', FF.r_tip_vec_full'], '.-k')
    end

    function plot_tree(trunk, branches, root_x, root_y, scale, style)
        hold on
        for i = 1:numel(trunk)
            quiver(root_x, root_y + trunk(i), branches(i), 0, scale, style)
        end
    end

end