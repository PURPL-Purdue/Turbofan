% Combines all the generation functions
function blade = pritchardCurves(x, y, betas, R_LE, R_TE, o, res)
    blade = pritchardArcs(x, y, betas, R_LE, R_TE, res);
    [blade.x_pressure, blade.y_pressure, blade.ps_p1x, blade.ps_p1y,     blade.k_max_ps] = pressure_bezier(x, y, betas, res);
    [blade.x_suction, blade.y_suction,          blade.x_spline_pts, blade.y_spline_pts,         blade.k_max_ss, blade.norm_x, blade.norm_y, blade.suction_curvature] = spliny_the_elder(x, y, betas, res);
    [blade.x_o, blade.y_o] = generate_throat(x, y, betas, o);
end

% Generates bezier curve for pressure side
function [x_pressure, y_pressure, ps_p1x, ps_p1y, k_max_ps] = pressure_bezier(x, y, betas, res)
    % Tangent Line Equations at Points 4 and 5
    syms x_perp
    % Slopes
    p4_slope = tan(betas(4));
    p5_slope = tan(betas(5));
    % Tangent Line Equations
    x4_perpendicular_sym = p4_slope*(x_perp-x(4))+y(4);
    x5_perpendicular_sym = p5_slope*(x_perp-x(5))+y(5);

    % Intersection of tangent lines to find P1's
    ps_p1x = double(vpasolve(x4_perpendicular_sym == x5_perpendicular_sym, x_perp));
    ps_p1y = double(subs(x4_perpendicular_sym, x_perp, ps_p1x));

    % Bezier for pressure side
    t = linspace(0,1,100*res);
    b0 = (1-t).^2;
    b1 = 2*t.*(1-t);
    b2 = t.^2;
    x_pressure = x(4)*b0 + ps_p1x*b1 + x(5)*b2;
    y_pressure = y(4)*b0 + ps_p1y*b1 + y(5)*b2;

    P0 = [x(4), y(4)];
    P1 = [ps_p1x, ps_p1y];
    P2 = [x(5), y(5)];
    
    % First derivatives
    dx_dt = 2*(1-t) * (P1(1)-P0(1)) + 2*t*(P2(1)-P1(1));
    dy_dt = 2*(1-t) * (P1(2)-P0(2)) + 2*t*(P2(2)-P1(2));
    
    % Second derivatives
    d2x_dt2 = 2*(P2(1) - 2*P1(1)+P0(1));
    d2y_dt2 = 2*(P2(2) - 2*P1(2)+P0(2));
    
    pressure_curvature = abs(dx_dt .* d2y_dt2 - dy_dt .* d2x_dt2) ./ (dx_dt.^2 + dy_dt.^2).^(3/2);
    pressure_curvature = rmoutliers(pressure_curvature, "mean");
    k_max_ps = max(abs(pressure_curvature));
end

% Generates B-Spline curve for suction side
function [x_suction, y_suction, x_spline_pts, y_spline_pts, k_max_ss, norm_x, norm_y, suction_curvature] = spliny_the_elder(x, y, betas, res)
    % Tangent Line Equations at Points 1, 2, and 3
    syms x_perp
    % Slopes
    p1_slope = tan(betas(1));
    p2_slope = tan(betas(2));
    p3_slope = tan(betas(3));
    % Tangent Line Equations
    x1_tan_sym = p1_slope*(x_perp-x(1))+y(1);
    x2_tan_sym = p2_slope*(x_perp-x(2))+y(2);
    x3_tan_sym = p3_slope*(x_perp-x(3))+y(3);

    % Intersection of tangent lines to find control points
    ss_12x = double(vpasolve(x1_tan_sym == x2_tan_sym, x_perp));
    ss_12y = double(subs(x1_tan_sym, x_perp, ss_12x));
    ss_23x = double(vpasolve(x2_tan_sym == x3_tan_sym, x_perp));
    ss_23y = double(subs(x2_tan_sym, x_perp, ss_23x));

    % Setting additional right side tangent handle
    handle_xlength = 0.001;
    right_handle_x = x(2)+handle_xlength;
    right_handle_y = double(subs(x2_tan_sym, x_perp, right_handle_x));
    left_handle_x = x(2)-handle_xlength;
    left_handle_y = double(subs(x2_tan_sym, x_perp, left_handle_x));

    % Gathering control points
    x_spline_pts = [x(3), x(3), x(3), x(3), x(3), ss_23x,    left_handle_x,     x(2), x(2), x(2), x(2), x(2),   right_handle_x,   ss_12x, x(1), x(1), x(1), x(1), x(1)];
    y_spline_pts = [y(3), y(3), y(3), y(3), y(3), ss_23y,    left_handle_y,     y(2), y(2), y(2), y(2), y(2),   right_handle_y,   ss_12y, y(1), y(1), y(1), y(1), y(1)];

    % Defining the B-Spline
    ctrlp = [x_spline_pts; y_spline_pts];
    knots = aptknt(x_spline_pts, 6);
    ss_spline = spmak(knots, ctrlp);

    % Generating plottable spline
    t_range = fnbrk(ss_spline, "interval");
    t = linspace(t_range(1), t_range(2), 100*res);
    spline_coords = fnval(ss_spline, t);
    dev1 = fnval(fnder(ss_spline, 1), t);
    dev2 = fnval(fnder(ss_spline, 2), t);

    x_suction = flip(spline_coords(1,:));
    y_suction = flip(spline_coords(2,:));

    % Compute curvature
    dev1_x = flip(dev1(1,:)); dev1_y = flip(dev1(2,:));
    dev2_x = flip(dev2(1,:)); dev2_y = flip(dev2(2,:));
    suction_curvature = (dev1_x.*dev2_y - dev1_y.*dev2_x) ./ (dev1_x.^2+dev1_y.^2).^(3/2);

    % Get normal vectors scaled
    mag = sqrt(dev1_x.^2 + dev1_y.^2);
    norm_x = -dev1_y ./ mag;  % rotate tangent by 90 degrees to get orthogonal vector
    norm_y =  dev1_x ./ mag;
    
    % Scale normals by curvature
    scale = 1;  % Adjust for visuaq     l clarity
    norm_x = norm_x .* suction_curvature * scale;
    norm_y = norm_y .* suction_curvature * scale;

    % Removing outliers for accurate kurvature calculation
    suction_curvature = rmoutliers(suction_curvature, "mean");

    % Calculating Max Curvature
    k_max_ss = max(abs(suction_curvature));

end

% Generates the throat line
function [x_o, y_o] = generate_throat(x, y, betas, o)
    %% Throat Plotting
    o_slope = -1/tan(betas(2));                    % Gets perpendicular slope
    x_o = [x(2), x(2) + o*cos(atan(o_slope))];     % X-coords for throat plot
    y_o = o_slope.*(x_o-x(2))+y(2);                % Y-coords for throat plot
end

function blade = pritchardArcs(x, y, betas, R_LE, R_TE, res)
    [blade.LEx, blade.LEy] = arc(x(3) + R_LE * cos(pi/2 - betas(3)), y(3) - R_LE * sin(pi/2 - betas(3)), R_LE, x(3), x(4), y(3), y(4), 1, res);
    [blade.TEx, blade.TEy] = arc(x(1) + R_TE * cos(pi/2 - betas(1)), y(1) - R_TE * sin(pi/2 - betas(1)), R_TE, x(5), x(1), y(5), y(1), 1, res);
    % [blade.UGx, blade.UGy] = arc(x(6), y(6), R_new, x(1), x(2), y(1), y(2), 10000, res);
    blade.x = x;
    blade.y = y;
    blade.betas = betas;
end

% Helper function for generating arc coordinates
function [x_arc, y_arc] = arc(x,y,r, x1, x2, y1, y2, multiplier, res)
    start = atan2(y1-y,x1-x);
    stop = atan2(y2-y,x2-x);
    if start > stop
        stop = stop + 2 * pi;
    end
    theta = start:pi/(100*multiplier*res):stop;
    x_arc = r * cos(theta) + x;
    y_arc = r * sin(theta) + y;
end