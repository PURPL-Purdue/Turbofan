% Generates Points 1-5 and their betas
function [pts,failcode] = pritchardPoints(R, R_LE, R_TE, Cx, Ct, zeta, beta_IN, ep_IN, beta_OUT, ep_OUT, N_B, o)
    cont = 1;
    max_iter = 100;
    iter_counter = 0;
    failcode = "success!!";
    while cont
        %% Points 1-5 -> X,Y Coordinates and Tangent Angles
        % POINT ONE - Suction Surface Trailing Edge Tangency Point
        beta_1 = beta_OUT - ep_OUT;
        x1 = Cx - R_TE * (1 + sin(beta_1));
        y1 = R_TE * cos(beta_1);
        
        % POINT TWO - Suction Surface Throat Point
        beta_2 = beta_OUT - ep_OUT + zeta;
        x2 = Cx - R_TE + (o + R_TE) * sin(beta_2);
        y2 = 2*pi*R/N_B - (o + R_TE) * cos(beta_2);

        % POINT THREE - Suction Surface Leading Edge Tangency Point
        beta_3 = beta_IN + ep_IN;
        x3 = R_LE * (1 - sin(beta_3));
        if Ct == 0
            Ct = y2 + (x2-x3)/(beta_2-beta_3) * log(cos(beta_2)/cos(beta_3)) - R_LE * cos(beta_3);
        end
        y3 = Ct + R_LE * cos(beta_3);
        
        % POINT FOUR - Pressure Surface Leading Edge Tangency Point
        beta_4 = beta_IN - ep_IN;
        x4 = R_LE * (1 + sin(beta_4));
        y4 = Ct - R_LE * cos(beta_4);
        
        % POINT FIVE - Pressure Surface Trailing Edge Tangency Point
        beta_5 = beta_OUT + ep_OUT;
        x5 = Cx - R_TE * (1 - sin(beta_5));
        y5 = -R_TE * cos(beta_5);

        %% Iteration on ep_OUT, following method by Mansour
        syms x_perp;
        % Symbolic equation for the orthographic line at Point 1
        p1_slope = -1/tan(beta_1);
        x1_perpendicular_sym = p1_slope*(x_perp-x1)+y1;

        % Symbolic equation for the orthographic line at Point 2
        o_slope = -1/tan(beta_2);
        x2_perpendicular_sym = o_slope*(x_perp-x2)+y2;
    
        % Intersection of the two orthographic lines
        x01 = double(vpasolve(x1_perpendicular_sym == x2_perpendicular_sym, x_perp));
        y01 = double(subs(x1_perpendicular_sym, x_perp, x01));

        % Iterates on ep_OUT
        R_01 = sqrt((x1-x01)^2 + (y1-y01)^2);
        yy2 = y01 + sqrt(R_01^2 - (x2-x01)^2);
        delta = abs(yy2 - y2);
        if delta > 0.0001
            ep_OUT = ep_OUT * (y2/yy2);
        else
            cont = 0;
        end

        iter_counter = iter_counter + 1;
        if iter_counter > max_iter
            failcode = "ep_out didn't converge";
            break
        end
    end
    %% Struct Outputs
    pts.betas = [beta_1, beta_2, beta_3, beta_4, beta_5];
    pts.x_coords = [x1, x2, x3, x4, x5, x01];
    pts.y_coords = [y1, y2, y3, y4, y5, y01];
    pts.R_new = R_01;
    pts.Ct = Ct;
end