%% GENERATES BLADE GEOMETRY
function blade = pritchard_main(params)
    failcode = "success!!";
    max_iter = 300;

    params.beta_IN = deg2rad(params.beta_IN);
    params.beta_OUT = deg2rad(params.beta_OUT);
    params.ep_IN = deg2rad(params.ep_IN);
    params.ep_OUT = deg2rad(params.ep_OUT);
    params.zeta = deg2rad(params.zeta);   

    o = 2*pi*params.R/params.N_B*cos(params.beta_OUT)-2*params.R_TE;

    factor = 1;
    ttc = params.ttc/100;
    iter_counter = 0;
    while factor > params.iteration_threshold
        [pts, failcode] = pritchardPoints(params.R, params.R_LE, params.R_TE, params.Cx, params.Ct, params.zeta, params.beta_IN, params.ep_IN, params.beta_OUT, params.ep_OUT, params.N_B, o);
        try
            blade = pritchardCurves(pts.x_coords, pts.y_coords, pts.betas, params.R_LE, params.R_TE, o, params.res);
        catch
            warning("bro what the hell man")
            blade.failcode = "knots broken";
            return
        end
        [blade.x_comb, blade.y_comb] = combiner(blade);     % Combine separate sections into big x and y vectors (good for solidworks exporting later too)
    
        if params.Ct == 0
            params.Ct = pts.Ct;
        end
        [t_max, pos_ss, pos_ps] = max_t(blade);
        chord = sqrt(params.Ct^2 + params.Cx^2);
        factor = abs(t_max/chord-ttc);
        if factor > params.iteration_threshold
            params.Ct = params.Ct*(3+t_max/chord/ttc)/4;
        end

        iter_counter = iter_counter + 1;
        if iter_counter > max_iter
            failcode = "ttc didn't converge";
            break
        end
    end

    blade.x_thicc = [blade.x_pressure(pos_ps), blade.x_suction(pos_ss)];
    blade.y_thicc = [blade.y_pressure(pos_ps), blade.y_suction(pos_ss)];

    % Extra params
    blade.parameters.R = params.R;
    blade.parameters = params;
    blade.parameters.o = o;
    blade.parameters.pitch = 2*pi*params.R/params.N_B;
    blade.parameters.t_max = max_t(blade);
    blade.parameters.t_min = min_t(blade);
    if blade.parameters.t_min < 1
        failcode = "blade too thin";
    end
    blade.parameters.zweifel = (4*pi*params.R) / (params.Cx*params.N_B) * sin(params.beta_IN - params.beta_OUT) * cos(params.beta_OUT)/cos(params.beta_IN);
    blade.parameters.blockage_IN = 2*params.R_LE / (blade.parameters.pitch * cos(params.beta_IN))  * 100;
    blade.parameters.blockage_OUT = 2*params.R_TE / (blade.parameters.pitch * cos(params.beta_OUT)) * 100;
    blade.parameters.chord = sqrt(params.Ct^2 + params.Cx^2);
    blade.parameters.calc_ttc = blade.parameters.t_max/blade.parameters.chord;
    blade.parameters.pitch_to_chord = blade.parameters.pitch/blade.parameters.chord;
    blade.parameters.height_to_chord = blade.parameters.blade_height/blade.parameters.chord;

    blade.parameters.beta_IN = rad2deg(blade.parameters.beta_IN);
    blade.parameters.beta_OUT = rad2deg(blade.parameters.beta_OUT);
    blade.parameters.ep_IN = rad2deg(blade.parameters.ep_IN);
    blade.parameters.ep_OUT = rad2deg(blade.parameters.ep_OUT);
    blade.parameters.zeta = rad2deg(blade.parameters.zeta); 

    blade.failcode = failcode;
    % fprintf("-#-#-#-#-\n\n\n _/~~~\\_ \n  (O_o)  \n \\__|__/ \n    |    \n  _/ \\_  \n_________\n")
    % fprintf("-> ")
end

%% HELPER FUNCTIONS

% Calculates max blade thickness and its location
function [t_max, pos_ss, pos_ps] = max_t(blade)
    thiccnesses = zeros(1, length(blade.x_pressure));
    for i = 1:length(blade.x_pressure)
        thiccnesses(i) = min(vecnorm([blade.x_suction(i); blade.y_suction(i)] - [blade.x_pressure; blade.y_pressure]));
    end
    [t_max, pos_ss] = max(thiccnesses);
    [~, pos_ps] = min(vecnorm([blade.x_suction(pos_ss); blade.y_suction(pos_ss)] - [blade.x_pressure; blade.y_pressure]));
end

function [t_min, pos_ss, pos_ps] = min_t(blade)
    thiccnesses = zeros(1, length(blade.x_pressure));
    for i = 1:length(blade.x_pressure)
        thiccnesses(i) = min(vecnorm([blade.x_suction(i); blade.y_suction(i)] - [blade.x_pressure; blade.y_pressure]));
    end
    [t_min, pos_ss] = min(thiccnesses);
    [~, pos_ps] = min(vecnorm([blade.x_suction(pos_ss); blade.y_suction(pos_ss)] - [blade.x_pressure; blade.y_pressure]));
end

% Combines XY matricies into one big XY matrix
function [x_comb, y_comb] = combiner(blade)
    x_comb = [blade.LEx, blade.x_pressure, blade.TEx, blade.x_suction];
    y_comb = [blade.LEy, blade.y_pressure, blade.TEy, blade.y_suction];
end