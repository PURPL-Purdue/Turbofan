function flow_field = Compressor_Free_Vortex(rps, r_hub_vec_stages, r_tip_vec_stages, ang_vel, degR_m, rho_m_vec_stages, cp, R, T0_stages, m_dot_target, e_c, gamma)
    %% ======== Initial Values ========
    num_streamlines = 51; % how very odd (this number must be odd)
    full_vec_length = length(r_hub_vec_stages)*2-1;

    %% ======== Vector Creation and Initialization ========
    Ctheta_spans = cell(1, full_vec_length);
    z_spans      = cell(1, full_vec_length);
    rho_spans    = cell(1, full_vec_length);
    T_spans      = cell(1, full_vec_length);
    r_spans      = cell(1, full_vec_length);

    r_hub_vec_full = ones(1, full_vec_length);
    r_tip_vec_full = ones(1, full_vec_length);
    rho_m_vec_full = ones(1, full_vec_length);

    degR_spans = cell(1, length(r_hub_vec_stages)-1);

    for s = 1:length(r_hub_vec_stages)
        r_hub_vec_full(s*2-1) = r_hub_vec_stages(s);
        r_tip_vec_full(s*2-1) = r_tip_vec_stages(s);
        rho_m_vec_full(s*2-1) = rho_m_vec_stages(s);
    end

    %% ==== Constant Determination ========
    r_mean = (r_hub_vec_stages(1) + r_tip_vec_stages(1))/2;
    b = rps.Ctheta_1m/r_mean;
    a = r_mean * (rps.Ctheta_2m-b*r_mean);

    %% ======== Spanwise Flowfield Calculations + Annulus Sizing ========
    for s = 1:numel(r_tip_vec_stages)
        % ======== Upstream of Rotor ========
        r_tip_new = r_tip_vec_stages(s);
        r_hub_new = r_hub_vec_stages(s);

        m_dot_current = m_dot_target + 1;
        while abs(m_dot_target - m_dot_current) > 0.001
            rSpan = linspace(r_hub_new, r_tip_new, num_streamlines);
            CthetaSpan = CthetaSpan_station1(rSpan, b);
            zSpan = zSpan_station1(rSpan, rps, r_mean, b);
            TSpan   = T_spanwise(T0_stages(s), CthetaSpan, zSpan, cp);
            rhoSpan = rho_spanwise(rSpan, rho_m_vec_stages(s), a, b, TSpan, T0_stages(s), CthetaSpan, zSpan, cp, R, "upstream");
            T_1m = TSpan((1 + end)/2);
            rho_1m = rhoSpan((1 + end)/2);

            m_dot_current = mass_flow(rSpan, rhoSpan, zSpan);

            annulus_current = pi * (r_tip_new^2 - r_hub_new^2);
            annulus_new = annulus_current * m_dot_target / m_dot_current;

            syms h
            h = double(solve((r_mean+h)^2 - (r_mean-h)^2 == annulus_new/pi, h));
            r_hub_new = r_mean - h;
            r_tip_new = r_mean + h;
        end
        
        r_hub_vec_full(s*2-1) = r_hub_new;
        r_tip_vec_full(s*2-1) = r_tip_new;
        rho_m_vec_full(s*2-1) = rho_1m;
        
        Ctheta_spans{s*2-1} = CthetaSpan;
        z_spans{s*2-1}      = zSpan;
        rho_spans{s*2-1}    = rhoSpan;
        T_spans{s*2-1}      = TSpan;
        r_spans{s*2-1}      = rSpan;
        
        if s < numel(r_tip_vec_stages)
            % ======== Downstream of Rotor ========
            r_tip_new = (r_tip_vec_stages(s) + r_tip_vec_stages(s+1))/2;
            r_hub_new = (r_hub_vec_stages(s) + r_hub_vec_stages(s+1))/2;
    
            m_dot_current = m_dot_target + 1;
            while abs(m_dot_target - m_dot_current) > 0.001
                rSpan = linspace(r_hub_new, r_tip_new, num_streamlines);
                CthetaSpan = CthetaSpan_station2(rSpan, a, b);                     % Difference
                zSpan = zSpan_station2(rSpan, rps, r_mean, a, b);                      % Difference
                TSpan   = T_spanwise(T0_stages(s+1), CthetaSpan, zSpan, cp);      % index difference
                T_2m = TSpan((1 + end)/2);
    
                rho_2m = rho_1m * (T_2m/T_1m)^((1-gamma*(1-e_c)) / (gamma-1));
    
                rhoSpan = rho_spanwise(rSpan, rho_2m, a, b, TSpan, T0_stages(s+1), CthetaSpan, zSpan, cp, R, "downstream");   % index difference
    
                m_dot_current = mass_flow(rSpan, rhoSpan, zSpan);
    
                annulus_current = pi * (r_tip_new^2 - r_hub_new^2);
                annulus_new = annulus_current * m_dot_target / m_dot_current;
                
                syms h
                h = double(solve((r_mean+h)^2 - (r_mean-h)^2 == annulus_new/pi, h));
                r_hub_new = r_mean - h;
                r_tip_new = r_mean + h;
            end
    
            r_hub_vec_full(s*2) = r_hub_new;
            r_tip_vec_full(s*2) = r_tip_new;
            rho_m_vec_full(s*2) = rho_2m;
    
            Ctheta_spans{s*2} = CthetaSpan;
            z_spans{s*2}      = zSpan;
            rho_spans{s*2}    = rhoSpan;
            T_spans{s*2}      = TSpan;
            r_spans{s*2}      = rSpan;
    
    
            degR_spans{s} = (1 - b/ang_vel) - ((a/r_mean)/(ang_vel*r_mean)) ./ (2 * (rSpan ./ r_mean).^2);
        end
    end

    % figure(1); clf;
    % plot_tree(r_spans{1}, Ctheta_spans{1},  00, 00, 0.1, '-b')
    % plot_tree(r_spans{1}, z_spans{1},       20, 00, 0.1, '-k')
    % plot_tree(r_spans{2}, z_spans{2},       40, 00, 0.1, '-k')
    % plot_tree(r_spans{2}, Ctheta_spans{2},  60, 00, 0.1, '-b')

    %% ======== Return ========
    flow_field.Ctheta_spans    = Ctheta_spans;
    flow_field.z_spans         = z_spans;
    flow_field.rho_spans       = rho_spans;
    flow_field.T_spans         = T_spans;
    flow_field.r_spans         = r_spans;
    flow_field.r_hub_vec_full  = r_hub_vec_full;
    flow_field.r_tip_vec_full  = r_tip_vec_full;
    flow_field.rho_m_vec_full  = rho_m_vec_full;
    flow_field.degR_spans      = degR_spans;
    flow_field.num_stations    = full_vec_length;
    flow_field.num_streamlines = num_streamlines;

    %% Functions
    function m_dot = mass_flow(r, rho, zSpan)
        m_dot = 0;
        for i = 1:numel(r)-1
            rho_avg = (rho(i)   + rho(i+1))  /2;
            z_avg =   (zSpan(i) + zSpan(i+1))/2;
            A = pi*(r(i+1)^2 - r(i)^2);
            m_dot = m_dot + (rho_avg * z_avg * A);
        end
    end

    function rhoSpan = rho_spanwise(r, rho_m, a, b, T, T0, CthetaSpan, zSpan, cp, R, type)
        mid_index = (1+length(r))/2;
        rhoSpan = ones(size(r))*rho_m;

        % ==== Ong it's integration time ====
        for i = mid_index:length(r)-1
            dr = r(i+1)-r(i);
            if type == "upstream"
                dTT = (b^2 * r(i) * dr) ./ (cp*T0 - (zSpan(i)^2 + CthetaSpan(i)^2));
            elseif type == "downstream"
                dTT = (2*a*b/r(i) + a^2/r(i)^3 + b^2*r(i))*dr / (cp*T0 - (zSpan(i)^2 + CthetaSpan(i)^2));
            end
            drho = rhoSpan(i) * (1/R/T(i) * (CthetaSpan(i)^2./r(i))*dr - dTT);
            rhoSpan(i+1) = rhoSpan(i) + drho;
        end
        for i = mid_index:-1:2
            dr = r(i)-r(i-1);
            if type == "upstream"
                dTT = (b^2 * r(i) * dr) ./ (cp*T0 - (zSpan(i)^2 + CthetaSpan(i)^2));
            elseif type == "downstream"
                dTT = (2*a*b/r(i) + a^2/r(i)^3 + b^2*r(i))*dr / (cp*T0 - (zSpan(i)^2 + CthetaSpan(i)^2));
            end
            drho = rhoSpan(i) * (1/R/T(i) * (CthetaSpan(i)^2./r(i))*dr - dTT);
            rhoSpan(i-1) = rhoSpan(i) - drho;
        end
    end

    function T_span = T_spanwise(T0, CthetaSpan, zSpan, cp)
        T_span = T0 - (CthetaSpan.^2 + zSpan.^2)./(2*cp);
    end


    function zSpan_1 = zSpan_station1(r, rps, r_mean, b)
        zSpan_1 = rps.z_1m * sqrt(1 + 2*(b*r_mean/rps.z_1m)^2 * (1-(r.^2)/(r_mean^2)));
    end
    function zSpan_2 = zSpan_station2(r, rps, r_mean, a, b)
        zSpan_2 = rps.z_1m * sqrt(1 + 2*(b*r_mean/rps.z_1m)^2 * (1-(r.^2)/(r_mean^2)) - (4*a*b/(rps.z_1m^2))*log(r/r_mean));
    end
    function CthetaSpan_1 = CthetaSpan_station1(r, b)
        CthetaSpan_1 = b*r;
    end
    function CthetaSpan_2 = CthetaSpan_station2(r, a, b)
        CthetaSpan_2 = b.*r + a./r;
    end

    function plot_tree(trunk, branches, root_x, root_y, scale, style)
        hold on
        for i = 1:numel(trunk)
            quiver(root_x, root_y + trunk(i), branches(i), 0, scale, style)
        end
    end
end