classdef IFN
    properties
    end
    methods(Static)
        %% FUNCTIONS
        % Puts all the user input into one struct for easy parameter passing
        function input = blade_parameters(R, R_LE, R_TE, Cx, ttc, zeta, beta_IN, ep_IN, beta_OUT, ep_OUT, N_B, blade_height, V_mag_mid, name, res, iteration_threshold)
            input.R = R;
            input.R_LE = R_LE;
            input.R_TE = R_TE;
            input.Cx = Cx;
            input.Ct = 0;
            input.ttc = ttc;
            input.zeta = zeta;
            input.beta_IN = beta_IN;
            input.ep_IN = ep_IN;
            input.beta_OUT = beta_OUT;
            input.ep_OUT = ep_OUT;
            input.N_B = N_B;
            input.blade_height = blade_height;
            input.V_mag_mid = V_mag_mid;
            input.name = name;
            input.res = res;
            input.iteration_threshold = iteration_threshold;
        end
        
        % Generates a blade profile with complete info set
        function [full_blade, mid_profile_index, success] = generate_blade(params, num_interpolate)
            success = true;
            
            num_profiles = 2*num_interpolate+5;
            r_tip = params.R;
            r_hub = params.R-params.blade_height;
            r_mid = (r_tip + r_hub)/2;
            interpolate_HM = linspace(r_hub, r_mid, num_interpolate+2);
            interpolate_MT = linspace(r_mid, r_tip, num_interpolate+2);
            radii = [r_hub-20, r_hub, interpolate_HM(2:end-1), r_mid, interpolate_MT(2:end-1), r_tip, r_tip+5];
            
            % RADIAL EQUILIBRIUM
            stack(1:num_profiles) = params;
            for i = 1:num_profiles
                stack(i).beta_IN = IFN.rad_eq(stack(i).V_mag_mid, r_mid, params.beta_IN, radii(i));
                stack(i).beta_OUT = IFN.rad_eq(stack(i).V_mag_mid, r_mid, params.beta_OUT, radii(i));
                stack(i).R = radii(i);
            end
            
            stack(1).name = stack(1).name + " Hub Extension";
            stack(2).name = stack(2).name + " Hub";
            for j = 3:(2+num_interpolate)
                stack(j).name = stack(j).name + " Lower Interpolation";
            end
            stack(3+num_interpolate).name = stack(3+num_interpolate).name + " Mid";
            mid_profile_index = 3+num_interpolate;
            for j = (4+num_interpolate):(3+2*num_interpolate)
                stack(j).name = stack(j).name + " Upper Interpolation";
            end
            stack(end-1).name = stack(end-1).name + " Tip";
            stack(end).name = stack(end).name + " Tip Extension";
        
            % GENERATING GEOMETRY
            % full_blade(num_profiles) = struct();
            for i = num_profiles:-1:1
                try
                    full_blade(i) = pritchard_main(stack(i));
                catch
                    warning("??????????????")
                    success = false;
                    return
                end
                if full_blade(i).failcode == "knots broken"
                    success = false;
                    return
                end
                % full_blade(i).failcode = failcode;
            end
        
            % fprintf("done\n")
        
        end
        
        % Radial Equilibrium calculations
        function beta_target = rad_eq(V_mag_mid, r_mid, theta, r_target)
            V_theta_mid = V_mag_mid * sind(theta);
            K = V_theta_mid * r_mid;
            V_theta_target = K/r_target;
            beta_target = atand(V_theta_target/(V_mag_mid * cosd(theta)));
        end

        function gong()
            load gong.mat

            for i = 1:24
                if i == 21
                    soundsc(y, 16000); % ongongongongongong
                elseif i == 22
                    soundsc(y, 8000); % ongongongongongongongongongongongong
                elseif i == 23
                    soundsc(y, 4000); % ongongongongongongongongongongongong
                elseif i == 24
                    soundsc(y, 2000); % ongongongongongongongongongongongong
                else
                    soundsc(y, 32000); % ggggg
                pause(0.075)
                end
            end
        end
    end
end