import math as m
import numpy as np
import warnings
import pritchardPoints
import pritchardCurves
import REF_structs as REF

def deg2rad(degrees):
    radians = degrees/180*m.pi
    return(radians)

def rad2deg(radians):
    degrees = radians*180/m.pi
    return(degrees)

def pritchard_main(params):
    failcode = "success!"
    max_iter = 300

    REF.params.beta_IN = deg2rad(REF.params.beta_IN)
    REF.params.beta_OUT = deg2rad(REF.params.beta_OUT)
    REF.params.ep_IN = deg2rad(REF.params.ep_IN)
    REF.params.ep_OUT = deg2rad(REF.params.ep_OUT)
    REF.params.zeta = deg2rad(REF.params.zeta)

    o = 2 * m.pi * REF.params.R / REF.params.N_B * m.cos(REF.params.beta_OUT - 2 * REF.params.R_TE)

    factor = 1
    ttc = REF.params.ttc/100
    iter_counter = 0
    while factor > REF.params.iteration_threshold:
        [pts, failcode] = pritchardPoints(REF.params.R, REF.params.R_LE, REF.params.R_TE, 
                                          REF.params.Cx, REF.params.Ct, REF.params.zeta, 
                                          REF.params.beta_IN, REF.params.ep_IN, REF.params.beta_OUT, 
                                          REF.params.ep_OUT, REF.params.N_B, REF.params.o)
        try:
            blade = pritchardCurves(REF.pts.x_coords, REF.pts.y_coords, REF.pts.betas, 
                                    REF.params.R_LE, REF.params.R_TE, o, REF.params.res)
            
        except:
            warnings.warn("bro what the hell man")
            REF.blade.failcode = "knots broken"
            return
    
        REF.blade.x_comb, REF.blade.y_comb = combiner(blade)

        if REF.params.Ct ==0:
            REF.params.Ct = REF.pts.Ct
        
        [t_max, pos_ss, pos_ps] = max_t(blade)
        chord = m.sqrt((REF.params.Ct)**2 + REF.params.Cx**2)
        factor = abs(t_max/chord - ttc)

        if factor > REF.params.iteration_threshold:
            REF.params.Ct = REF.params.Ct * (3 + t_max / chord / ttc) / 4
        
        iter_counter += 1

        if iter_counter > max_iter:
            failcode = "ttc didn't converge"
            break
    
    REF.blade.x_thicc = REF.blade["x_pressure"[pos_ps - 1]], blade["x_suction"[pos_ss -1]]]  #are these two variables lists Im assuming?
    REF.blade.y_thicc = [blade["y_pressure"[pos_ps - 1]], blade["y_suction"[pos_ss-1]]]

    #Extra params
    REF.blade.parameters.R = REF.params.R
    REF.blade.parameters = REF.params
    REF.blade.parameters.o = o
    REF.blade.parameters.pitch = 2*m.pi*params["R"]/params["N_B"]
    REF.blade.parameters.t_max = max_t(blade)
    REF.blade.parameters.t_min = min_t(blade)
    if REF.blade.parameters.t_min < 1:
        failcode = "blade too thin"
    
    REF.blade.parameters.zweifel = (4*m.pi*REF.params.R) / (REF.params.Cx*REF.params.N_B) * m.sin(REF.params.beta_IN - REF.params.beta_OUT) * m.cos(REF.params.beta_OUT) / m.cos(REF.params.beta_IN)
    REF.blade.parameters.blockage_IN = 2 * REF.params.R_LE / REF.blade.params.pitch * m.cos(REF.params.beta_IN) * 100
    REF.blade.parameters.blockage_OUT = 2 * REF.params.R_TE / (REF.blade.parameters.pitch * m.cos(REF.params.beta_OUT) * 100)
    REF.blade.parameters.chord = m.sqrt(REF.params.Ct^2 + REF.params.Cx^2)
    REF.blade.parameters.calc_ttc = REF.blade.parameters.t_max / REF.blade.parameters.chord

    REF.blade.parameters.pitch_to_chord = REF.blade.parameters.pitch / REF.blade.parameters.chord    
    REF.blade.parameters.height_to_chord = REF.blade.parameters.blade_height/blade.parameters.chord
    REF.blade.parameters.beta_IN = rad2deg(REF.blade.parameters.beta_IN)
    REF.blade.parameters.beta_OUT = rad2deg(REF.blade.parameters.beta_OUT)
    REF.blade.parameters.ep_IN = rad2deg(REF.blade.parameters.ep_IN)
    REF.blade.parameters.ep_OUT = rad2deg(REF.blade.parameters.ep_OUT)
    REF.blade.parameters.zeta = rad2deg(REF.blade.parameters.zeta) 

    REF.blade.failcode = failcode
    return(blade)

    
#Helper Functions
    
#Calculates max blade thickness and its location
def max_t(blade):
    rows = 1
    cols = len(REF.blade.x_pressure)
    suction_array = np.array([REF.blade.x_suction[i], REF.blade.y_suction[i]])
    pressure_array = np.array([REF.blade.x_pressure, REF.blade.y_pressure])
    
    thiccnesses = [[0 for _ in range(cols)] for _ in range(rows)]
    for i in len(REF.blade.x_pressure):
        thiccnesses[i] = min(np.linalg.norm(suction_array - pressure_array))
    [t_max, pos_ss] = max(thiccnesses)


#rest of unconverted code
"""
    thiccnesses = zeros(1, length(blade.x_pressure))
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

"""