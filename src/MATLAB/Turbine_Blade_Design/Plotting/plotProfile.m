function plotProfile(blade, plot_throat, plot_t_max, plot_spline_controls, show_curvature, main_linestyle)
    hold on
    plot3(blade.x_comb,blade.y_comb, ones(1, length(blade.x_comb))*blade.parameters.R, main_linestyle, LineWidth=0.5)         % Curves!
    scatter3(blade.x, blade.y, ones(1, 6)*blade.parameters.R, 20, 'b', "filled")                                            % Points!!

    if show_curvature
        quiver(blade.x_suction, blade.y_suction, blade.norm_x, blade.norm_y, 0, 'r');       % curvature vectors
        scatter(blade.x_suction, blade.y_suction, 1, blade.suction_curvature, 'filled');            % Color-coded curvature points
        colorbar; colormap turbo;
    end
    if plot_throat
        line(blade.x_o, blade.y_o, [blade.parameters.R, blade.parameters.R], Color='blue', LineStyle='--')            % Throat!!!
    end
    if plot_t_max
        line(blade.x_thicc, blade.y_thicc, [blade.parameters.R, blade.parameters.R], Color='green', LineStyle='--')   % T-Max!!!!
    end
    if plot_spline_controls
        plot_bezier_fluff(blade);       % Bezier fluff!!!!!
        plot_spline_fluff(blade);       % Spline fluff!!!!!!
    end
end

function plot_bezier_fluff(blade)
    line([blade.x(4), blade.ps_p1x], [blade.y(4), blade.ps_p1y], [blade.parameters.R, blade.parameters.R], Color='red', LineStyle='--')
    line([blade.ps_p1x, blade.x(5)], [blade.ps_p1y, blade.y(5)], [blade.parameters.R, blade.parameters.R], Color='red', LineStyle='--')
    plot3(blade.ps_p1x, blade.ps_p1y, blade.parameters.R, '.b', MarkerSize=5)
end

function plot_spline_fluff(blade)
    plot3(blade.x_spline_pts,blade.y_spline_pts, ones(1, length(blade.x_spline_pts))*blade.parameters.R, '--r')
    plot3(blade.x_spline_pts, blade.y_spline_pts, ones(1, length(blade.x_spline_pts))*blade.parameters.R, '.b', MarkerSize=10)   
end