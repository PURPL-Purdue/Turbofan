%% Multiple Circular Arc 2D Blade Geometry Generator
% By PURPL Turbojet/Turbofan Compressor Team
clear;
clc;
%% Parameters Definition
% Blade geometry Inputs
c_tot = 1;                  % Total chord length
ac = 0.3;                   % Ratio of forward arc chord vs total chord
alpha_2 = 57.9834;               % Inlet absolute flow angle (degrees)
% yet to determine
beta_1 = -48.2229;          % Inlet relative flow angle (degrees)
inc = 2;                    % Incidence angle (degrees)
t_max = 0.10 * c_tot;       % Maximum thickness (10% of chord)
t_BA  = 0.015 * c_tot;      % Leading edge thickness
t_BF  = 0.010 * c_tot;      % Trailing edge thickness
% Cascade inputs
solidity_R = 1;             % Rotor Solidity 
solidity_S = 1.25;          % Stator Solidity 
n_blades = 3;               % Number of blades plotted in the cascades
gap_ratio = 0.3;            % Axial gap / chord (rotor TE -> stator LE)
% Scale blade
chord_mm = 50;              % Scale the chord length [mm]
% Geometry generation point sets
theta = linspace(0, 2*pi, 25); % Angle range set used in circle generation
N = 25;                        % Number of points used in Arc generation
%% Calculations
% Inlet metal angles
k1_S = alpha_2 - inc; % Stator inlet metal angle [degrees]
k1_R = sign(beta_1)*(abs(beta_1) - inc); % Rotor inlet metal angle [degrees]
% Generate Stator and Rotor blades
stator = mcaBlade(k1_S, ac, c_tot, t_max, t_BA, t_BF, theta, N);
rotor  = mcaBlade(k1_R, ac, c_tot, t_max, t_BA, t_BF, theta, N);
foil_S = stator.foil_s; % Staggered stator blade outline
foil_R = rotor.foil_s; % Staggered rotor blade outline 
% Unpack stator variables for the construction figures
k1 = stator.k1;  k2 = stator.k2;  stagger = stator.stagger;
foil = stator.foil;  foil_s = stator.foil_s;
cLE = stator.cLE;  cTE = stator.cTE;  cMax = stator.cMax;
cLE_s = stator.cLE_s;  cTE_s = stator.cTE_s;  cMax_s = stator.cMax_s;
cVLE_plot = stator.cVLE_plot;  cVTE_plot = stator.cVTE_plot;
ext_f = stator.ext_f;  int_f = stator.int_f;  ext_r = stator.ext_r;  int_r = stator.int_r;
x_tr = stator.x_tr;
% Mirrored arc data for the virtual symmetric profiles
ext_f_mir_x = 2*x_tr - ext_f.x;
int_f_mir_x = 2*x_tr - int_f.x;
ext_r_mir_x = 2*x_tr - ext_r.x;
int_r_mir_x = 2*x_tr - int_r.x;
%% Plotting
% MCA blade construction
figure(1);
% Plot base blade geometry
plot(foil(1,:), foil(2,:), "k", LineWidth=2);
hold on;
% Plot LE,TE, and max thickness circles
plot(cLE(1,:), cLE(2,:),  "b", LineWidth=2);
plot(cTE(1,:), cTE(2,:), "b", LineWidth=2);
plot(cMax(1,:), cMax(2,:), "k:");
% Plot virtual circles and their helper arcs
plot(cVLE_plot(1,:), cVLE_plot(2,:), "r", LineWidth=2);
plot(cVTE_plot(1,:), cVTE_plot(2,:), "r", LineWidth=2);
plot([ext_f.x, fliplr(ext_f_mir_x)], [ext_f.y, fliplr(ext_f.y)], "g:", LineWidth=1.35);
plot([int_f.x, fliplr(int_f_mir_x)], [int_f.y, fliplr(int_f.y)], "g:", LineWidth=1.35);
plot([ext_r.x, fliplr(ext_r_mir_x)], [ext_r.y, fliplr(ext_r.y)], "m:", LineWidth=1.35);
plot([int_r.x, fliplr(int_r_mir_x)], [int_r.y, fliplr(int_r.y)], "m:", LineWidth=1.35);
hold off;
xlabel("Axial Direction ($z$)", 'Interpreter','latex');
ylabel("Tangential Direction ($\theta$)", 'Interpreter','latex');
title("MCA Blade Geometry Construction");
axis equal;
grid on;
% Staggered stator blade
figure(2);
plot(foil_s(1,:), foil_s(2,:));
hold on;
plot(cLE_s(1,:), cLE_s(2,:),  'k:');
plot(cTE_s(1,:), cTE_s(2,:), 'k:');
plot(cMax_s(1,:), cMax_s(2,:), 'k:');
hold off;
xlabel("Axial Direction ($z$)", 'Interpreter','latex');
ylabel("Tangential Direction ($\theta$)", 'Interpreter','latex');
title(sprintf("MCA Blade Geometry - Stator Stagger = %.2f°", stator.stagger));
axis equal;
grid on;
%% Deviation Angle determination (Carter's Rule, per row)
m = @(g) 0.216 + 0.000875.*g + 0.00002625.*(g.^2);   % Empirical constant

phi_S = stator.k1 - stator.k2;                % Camber angle [degrees]
m_S   = m(stator.stagger);
delta_S   = m_S.*phi_S./sqrt(solidity_S);     % Deviation angle (Stator) [degrees]
epsilon_S = phi_S + inc - delta_S;            % Fluid deflection (Stator) [degrees]

phi_R = abs(rotor.k1 - rotor.k2);             % Camber angle magnitude (rotor is mirrored)
m_R   = m(abs(rotor.stagger));
delta_R   = m_R.*phi_R./sqrt(solidity_R);     % Deviation angle (Rotor) [degrees]
epsilon_R = phi_R + inc - delta_R;            % Fluid deflection (Rotor) [degrees]
%% Rotor Cascade
pitch_R = c_tot ./ solidity_R;                % blade-to-blade spacing (tangential direction)
figure(3); hold on;
for j = 0:n_blades-1
    plot(foil_R(1,:), foil_R(2,:) + j*pitch_R);
end
hold off;
xlabel("Axial Direction ($z$)", 'Interpreter','latex');
ylabel("Tangential Direction ($\theta$)", 'Interpreter','latex');
title(sprintf("Rotor Cascade - Stagger = %.2f°, Solidity = %.2f", rotor.stagger, solidity_R));
axis equal;
grid on;
%% Stator Cascade
pitch_S = c_tot ./ solidity_S;  % blade-to-blade spacing (tangential direction)
figure(4); hold on;
for j = 0:n_blades-1
    plot(foil_S(1,:), foil_S(2,:) + j*pitch_S);
end
hold off;
xlabel("Axial Direction ($z$)", 'Interpreter','latex');
ylabel("Tangential Direction ($\theta$)", 'Interpreter','latex');
title(sprintf("Stator Cascade - Stagger = %.2f°, Solidity = %.2f", stator.stagger, solidity_S));
axis equal;
grid on;
%% Stage
gap = gap_ratio.*c_tot; % Axial gap, rotor TE -> stator LE
x_shift = max(foil_R(1,:)) + gap - min(foil_S(1,:)); % places the stator after the rotor
figure(5);
hold on;
for j = 0:n_blades-1
    plot(foil_R(1,:), foil_R(2,:) + j*pitch_R);
    plot(foil_S(1,:) + x_shift, foil_S(2,:) + j*pitch_S);
end
hold off;
xlabel("Axial Direction ($z$)", 'Interpreter','latex');
ylabel("Tangential Direction ($\theta$)", 'Interpreter','latex');
title("HPCA Stage");
axis equal;
grid on;
%% Helper functions
function B = mcaBlade(k1, ac, c_tot, t_max, t_BA, t_BF, theta, N)
    % Builds one MCA blade for inlet metal angle k1.
    % A negative k1 builds the mirror image (pressure side up, negative stagger).
    sgn = sign(k1);  k1 = abs(k1);     % build with a positive angle, mirror at the end if negative
    %% Camber line
    C_AE_Axial = c_tot.*ac;
    R_cambAE = C_AE_Axial./sind(k1);
    y_cambAE = -C_AE_Axial./tand(k1);
    k2 = atand((2.*(1-ac).*c_tot.*R_cambAE.*(1-cosd(k1)))./...
        abs(-((1-ac).*c_tot).^2 + (R_cambAE.*(1-cosd(k1))).^2));
    stagger = (k1 + k2)./2;
    %% LE and TE circles
    r_BA = t_BA./2;  r_BF = t_BF./2;
    x_BA = r_BA;  y_BA = 0;
    x_BF = c_tot; y_BF = 0;
    %% Max thickness circle (centered on the camber line at the transition)
    x_tr  = C_AE_Axial + r_BA;
    h     = y_cambAE + R_cambAE;
    r_max = t_max/2;
    cLEc  = [x_BA, y_BA, r_BA];
    cTEc  = [x_BF, y_BF, r_BF];
    cMaxc = [x_tr, h, r_max];
    cVTE  = [2*x_tr - x_BA, y_BA, r_BA];   % LE circle mirrored about x = x_tr
    cVLE  = [2*x_tr - x_BF, y_BF, r_BF];   % TE circle mirrored about x = x_tr
    %% Arcs (Apollonius)
    [ext_f, int_f] = mcaArc(cLEc, cMaxc, cVTE, N);
    [ext_r, int_r] = mcaArc(cTEc, cMaxc, cVLE, N);
    cLE  = [x_BA + r_BA*cos(theta);  y_BA + r_BA*sin(theta)];
    cTE  = [x_BF + r_BF*cos(theta);  y_BF + r_BF*sin(theta)];
    cMax = [x_tr + r_max*cos(theta); h + r_max*sin(theta)];
    cVLE_plot = [cVLE(1) + cVLE(3)*cos(theta); cVLE(2) + cVLE(3)*sin(theta)];
    cVTE_plot = [cVTE(1) + cVTE(3)*cos(theta); cVTE(2) + cVTE(3)*sin(theta)];
    suc_arc = [ext_f.x, ext_r.x(end-1:-1:1); ext_f.y, ext_r.y(end-1:-1:1)];
    prs_arc = [int_f.x, int_r.x(end-1:-1:1); int_f.y, int_r.y(end-1:-1:1)];
    %% Tip points from the existing circles
    ang = @(x, y, xc, yc) mod(atan2(y - yc, x - xc), 2*pi);
    phLE_s = ang(ext_f.x(1), ext_f.y(1), x_BA, y_BA);
    phLE_p = ang(int_f.x(1), int_f.y(1), x_BA, y_BA);
    phTE_s = ang(ext_r.x(1), ext_r.y(1), x_BF, y_BF);
    phTE_p = ang(int_r.x(1), int_r.y(1), x_BF, y_BF);
    LE_s = fliplr(cLE(:, theta >= phLE_s & theta <= pi));
    LE_p = cLE(:, theta > pi & theta <= phLE_p);
    TE_s = fliplr(cTE(:, theta <= phTE_s));
    TE_p = cTE(:, theta >= phTE_p);
    suc = [LE_s, suc_arc, TE_s];
    prs = [LE_p, prs_arc, TE_p];
    %% Full airfoil point set (closed loop, counter-clockwise)
    % pressure side nose -> tail, then suction side tail -> nose.
    foil = [prs, fliplr(suc(:, 1:end-1))];
    %% Stagger rotation about LE point
    x_LE = r_BA - r_BA*cos(pi/4);
    y_LE = -r_BA*sin(pi/4);
    Rot   = [cosd(stagger), -sind(stagger); sind(stagger), cosd(stagger)];
    pivot = [x_LE; y_LE];
    rot   = @(P) Rot*(P - pivot) + pivot;
    %% Output (mirror about the horizontal line through the LE pivot if the inlet angle was negative)
    foil_s = rot(foil);
    cLE_s = rot(cLE);  cTE_s = rot(cTE);  cMax_s = rot(cMax);
    if sgn < 0
        flip = @(P) [P(1,:); 2*pivot(2) - P(2,:)];
        foil   = fliplr(flip(foil));    foil_s = fliplr(flip(foil_s));   % reversed order keeps counter-clockwise ordering
        cLE = flip(cLE);  cTE = flip(cTE);  cMax = flip(cMax);
        cLE_s = flip(cLE_s);  cTE_s = flip(cTE_s);  cMax_s = flip(cMax_s);
        k1 = -k1;  k2 = -k2;  stagger = -stagger;
    end
    B = struct('k1',k1, 'k2',k2, 'stagger',stagger, 'pivot',pivot, 'x_tr',x_tr, ...
               'foil',foil, 'foil_s',foil_s, ...
               'cLE',cLE, 'cTE',cTE, 'cMax',cMax, ...
               'cLE_s',cLE_s, 'cTE_s',cTE_s, 'cMax_s',cMax_s, ...
               'cVLE_plot',cVLE_plot, 'cVTE_plot',cVTE_plot, ...
               'ext_f',ext_f, 'int_f',int_f, 'ext_r',ext_r, 'int_r',int_r);
end
function [extr, intr] = mcaArc(cReal, cMax, cVirt, N)
    % One Apollonius solve -> both surfaces for this portion of the blade.
    % Positive root = internal tangency (extrados), negative root = external (intrados).
    sol = apolloniusRoots(cReal, cMax, cVirt);     % rows: [rs, xs, ys]
    kE = sol(:,1) > 0;
    kI = sol(:,1) < 0;
    extr = buildArc(sol(kE,:), cReal, cMax, N);
    intr = buildArc(sol(kI,:), cReal, cMax, N);
end

function arc = buildArc(row, cReal, cMax, N)
    % Arc from the tangent point on cReal to the tangent point on cMax
    R  = abs(row(1));  xc = row(2);  yc = row(3);
    th1 = atan2(cReal(2) - yc, cReal(1) - xc);     % tangent point lies on the center line
    th2 = atan2(cMax(2)  - yc, cMax(1)  - xc);
    ang = linspace(th1, th2, N);
    arc = struct('R', R, 'xc', xc, 'yc', yc, ...
                 'x', xc + R*cos(ang), 'y', yc + R*sin(ang));
end

function sol = apolloniusRoots(c1, c2, c3)
    % Apollonius' problem with s1 = s2 = s3 = 1: (x-xi)^2 + (y-yi)^2 = (rs - ri)^2
    % Subtracting eq.1 from eq.2 and eq.3 gives x_s, y_s linear in r_s (eqs. 14-19),
    % then substituting into eq.1 gives a*rs^2 + b*rs + c = 0 (eq. 20).
    x1 = c1(1); y1 = c1(2); r1 = c1(3);
    x2 = c2(1); y2 = c2(2); r2 = c2(3);
    x3 = c3(1); y3 = c3(2); r3 = c3(3);

    M = x2^2 + y2^2 - r2^2 - x1^2 - y1^2 + r1^2;   % note: -r2^2 + r1^2
    N = 2*(r2 - r1);
    P = x3^2 + y3^2 - r3^2 - x1^2 - y1^2 + r1^2;
    Q = 2*(r3 - r1);

    k   = (x2 - x1)/(x3 - x1);
    den = 2*(y2 - y1) - 2*(y3 - y1)*k;
    S = (M - P*k)/den;
    T = (N - Q*k)/den;
    U = (P - S*2*(y3 - y1))/(2*(x3 - x1));
    V = (Q - T*2*(y3 - y1))/(2*(x3 - x1));

    a = V^2 + T^2 - 1;
    b = 2*(U*V + S*T - x1*V - y1*T + r1);
    c = x1^2 + y1^2 + U^2 + S^2 - r1^2 - 2*(x1*U + y1*S);

    rs  = real(roots([a, b, c]));
    sol = [rs, U + V*rs, S + T*rs];
end
%% Export Blade Geometry (Stator & Rotor)
scale = chord_mm / c_tot;
pts_stator = [foil_S; zeros(1, size(foil_S,2))].' * scale;
pts_rotor  = [foil_R; zeros(1, size(foil_R,2))].' * scale;
writematrix(pts_stator, 'stator_outline.txt', 'Delimiter', 'space');
writematrix(pts_rotor,  'rotor_outline.txt',  'Delimiter', 'space');