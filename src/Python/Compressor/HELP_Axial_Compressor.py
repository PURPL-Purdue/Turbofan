import numpy as np
import math as m

from Reference import REF_AEQ
from Reference import REF_structs

def Compressor_Free_Vortex(rps, r_hub_vec_stages, r_tip_vec_stages, ang_vel, degR_m, rho_m_vec_stages, cp, R, T0_stages, m_dot_target, e_c, gamma):
    ## ======== Initial Values ========
    num_streamlines = 51 # how very odd (this number must be odd to ensure we actually have an integer middle index)
    full_vec_length = len(r_hub_vec_stages)*2-1 # Total number of stations for all the stages

    ## ======== Vector Creation and Initialization ========
    Ctheta_spans = [[] for _ in range(full_vec_length)]
    z_spans      = [[] for _ in range(full_vec_length)]
    rho_spans    = [[] for _ in range(full_vec_length)]
    T_spans      = [[] for _ in range(full_vec_length)]
    r_spans      = [[] for _ in range(full_vec_length)]

    r_hub_vec_full = [1 for _ in range(full_vec_length)]
    r_tip_vec_full = [1 for _ in range(full_vec_length)]
    rho_m_vec_full = [1 for _ in range(full_vec_length)]

    degR_spans = [[] for _ in range(len(r_hub_vec_stages)-1)]

    for s in range(len(r_hub_vec_stages)): # Populating full arrays with stage starting parameters
        r_hub_vec_full[s*2] = r_hub_vec_stages[s]
        r_tip_vec_full[s*2] = r_tip_vec_stages[s]
        rho_m_vec_full[s*2] = rho_m_vec_stages[s]

    ## ==== Constant Determination ========
    r_mean = (r_hub_vec_stages[0] + r_tip_vec_stages[0])/2
    b = rps.Ctheta_1m/r_mean
    a = r_mean * (rps.Ctheta_2m-b*r_mean)

    ## ======== Spanwise Flowfield Calculations + Annulus Sizing ========
    # Mathmatical process taken from Farokhi 8.6.5.1
    # Equations taken from Farokhi are numbered where they appear
    for s in range(len(r_tip_vec_stages)): # For each stage
        # ======== Station 2: Upstream of Rotor ========
        r_tip_new = r_tip_vec_stages[s]     # Set initial annulus radii guesses
        r_hub_new = r_hub_vec_stages[s]

        m_dot_current = m_dot_target + 1
        while np.abs(m_dot_target - m_dot_current) > 0.001:
            rSpan = np.linspace(r_hub_new, r_tip_new, num_streamlines)
            CthetaSpan = CthetaSpan_station1(rSpan, b)
            zSpan = zSpan_station1(rSpan, rps, r_mean, b)
            TSpan   = T_spanwise(T0_stages[s], CthetaSpan, zSpan, cp)
            rhoSpan = rho_spanwise(rSpan, rho_m_vec_stages[s], a, b, TSpan, T0_stages[s], CthetaSpan, zSpan, cp, R, "upstream") # TODO
            T_1m = TSpan[len(TSpan)//2]
            rho_1m = rhoSpan[len(rhoSpan)//2]

            m_dot_current = mass_flow(rSpan, rhoSpan, zSpan)

            annulus_current = np.pi * (r_tip_new**2 - r_hub_new**2) # Geometry
            annulus_new = annulus_current * m_dot_target / m_dot_current

            # Obtaining updated annulus radii
            h = annulus_new/(4*r_mean*np.pi)
            r_hub_new = r_mean - h
            r_tip_new = r_mean + h
        
        # Updating arrays
        r_hub_vec_full[s*2] = r_hub_new
        r_tip_vec_full[s*2] = r_tip_new
        rho_m_vec_full[s*2] = rho_1m
        
        Ctheta_spans[s*2] = CthetaSpan
        z_spans[s*2]      = zSpan
        rho_spans[s*2]    = rhoSpan
        T_spans[s*2]      = TSpan
        r_spans[s*2]      = rSpan
        
        # ======== Station 3: Downstream of Rotor ========
        if s < len(r_tip_vec_stages)-1: # Excludes last 'fake' stage
            r_tip_new = (r_tip_vec_stages[s] + r_tip_vec_stages[s+1])/2
            r_hub_new = (r_hub_vec_stages[s] + r_hub_vec_stages[s+1])/2
    
            m_dot_current = m_dot_target + 1
            while abs(m_dot_target - m_dot_current) > 0.001:
                rSpan = np.linspace(r_hub_new, r_tip_new, num_streamlines)
                CthetaSpan = CthetaSpan_station2(rSpan, a, b)                       # [8.126]
                zSpan = zSpan_station2(rSpan, rps, r_mean, a, b)
                TSpan   = T_spanwise(T0_stages[s+1], CthetaSpan, zSpan, cp)
                
                T_2m = TSpan[len(TSpan)//2]
                rho_2m = rho_1m * (T_2m/T_1m)**((1-gamma*(1-e_c)) / (gamma-1))      # [8.150]
                
                rhoSpan = rho_spanwise(rSpan, rho_2m, a, b, TSpan, T0_stages[s+1], CthetaSpan, zSpan, cp, R, "downstream")
    
                m_dot_current = mass_flow(rSpan, rhoSpan, zSpan)
    
                annulus_current = np.pi * (r_tip_new**2 - r_hub_new**2)
                annulus_new = annulus_current * m_dot_target / m_dot_current
                
                # Calculating updated annulus radii
                h = annulus_new/(4*r_mean*np.pi)
                r_hub_new = r_mean - h
                r_tip_new = r_mean + h
    
            # Updating vectors
            r_hub_vec_full[s*2+1] = r_hub_new
            r_tip_vec_full[s*2+1] = r_tip_new
            rho_m_vec_full[s*2+1] = rho_2m
    
            Ctheta_spans[s*2+1] = CthetaSpan
            z_spans[s*2+1]      = zSpan
            rho_spans[s*2+1]    = rhoSpan
            T_spans[s*2+1]      = TSpan
            r_spans[s*2+1]      = rSpan
    
            # Degree of Reaction spanwise distribution (per stage)
            degR_spans[s] = (1 - b/ang_vel) - ((a/r_mean)/(ang_vel*r_mean)) / (2 * (rSpan / r_mean)**2) # [8.135]

    # ======== Return ========
    flow_field = REF_structs.CompressorField(
        Ctheta_spans,
        z_spans,
        rho_spans,
        T_spans,
        r_spans,
        r_hub_vec_full,
        r_tip_vec_full,
        rho_m_vec_full,
        degR_spans,
        full_vec_length,
        num_streamlines
    )

    return flow_field

def Blade_Root_Stress():
    pass

def Blade_Bending_Stress(ang_vel, r_tip_vec_full, r_hub_vec_full, taper_ratio, r_mean_1):
    flow_area = 2 * (m.pi) * r_mean_1 * (r_tip_vec_full - r_hub_vec_full)
    blade_stress = ((ang_vel**2) * flow_area / (4 * m.pi)) * (1 + taper_ratio) * rho_titanium  #equations for flow area and blade stress taken from Farokhi 669
    #are taper_ratio, ang_vel rho_titanium set?
    #used the r_mean_1 parameter from ref structs
    # do i need to return anything other than blade stress? do we need flow area anywhere?
    # do any of these variables need to be added to REF structs?
    pass
    return(blade_stress)

## Helper Functions
def D_factor(W1, W2, Ctheta_1, Ctheta_2, sigma):
        # Diffusion factor, generally should be greater than 0.55 to prevent boundary layer separation
        D = 1- W2/W1 + abs(Ctheta_1 - Ctheta_2)/(2*sigma*W1)
        return D

def annulus_adjust(T0, P0, R, gamma, m_dot, z, Mc, r_mean):
        # Adjusts the annulus at a given station to meet mass flow rate
        T = T0 * REF_AEQ.T_T0(gamma, Mc) # | spanwise constant (design choice i think)
        P = P0 * REF_AEQ.P_P0(gamma, Mc) # | spanwise constant (design choice i think)
        rho_m = P/(R*T)

        A = m_dot/(rho_m*z)
        h = A / (4 * np.pi * r_mean)

        r_hub = r_mean - h
        r_tip = r_mean + h
    
        return [r_hub, r_tip, rho_m]

def mass_flow(r, rho, zSpan):
    # Numeric integration to calculate mass flow rate at a given axial location
    m_dot = 0
    for i in range(len(r)-1):
        rho_avg = (rho[i]   + rho[i+1])  /2
        z_avg =   (zSpan[i] + zSpan[i+1])/2
        A = np.pi*(r[i+1]**2 - r[i]**2)
        m_dot = m_dot + (rho_avg * z_avg * A)
    return (m_dot)

def rho_spanwise(r, rho_m, a, b, T, T0, CthetaSpan, zSpan, cp, R, type):
    mid_index = len(r)//2
    rhoSpan = [rho_m for _ in range(len(r))]

    # ==== Ong it's integration time ====
    # Numeric integration (the larger num_streamlines is, the more accurate this process is)
    # Process taken from Farokhi P.580-582
    for i in range(mid_index, len(r)-1):
        dr = r[i+1]-r[i]
        if type == "upstream":
            dTT = (b**2 * r[i] * dr) / (cp*T0 - (zSpan[i]**2 + CthetaSpan[i]**2))                           # [8.143]
        elif type == "downstream":
            dTT = (2*a*b/r[i] + a**2/r[i]**3 + b**2*r[i])*dr / (cp*T0 - (zSpan[i]**2 + CthetaSpan[i]**2))   # [A lot of math that I forget how I did :skull:, refer to P.581]
        drho = rhoSpan[i] * (1/R/T[i] * (CthetaSpan[i]**2/r[i])*dr - dTT)                                   # [8.140]
        rhoSpan[i+1] = rhoSpan[i] + drho
    for i in range(mid_index,1,-1):
        dr = r[i]-r[i-1]
        if type == "upstream":
            dTT = (b**2 * r[i] * dr) / (cp*T0 - (zSpan[i]**2 + CthetaSpan[i]**2))                           # [8.143]
        elif type == "downstream":
            dTT = (2*a*b/r[i] + a**2/r[i]**3 + b**2*r[i])*dr / (cp*T0 - (zSpan[i]**2 + CthetaSpan[i]**2))   # [P.581]
        drho = rhoSpan[i] * (1/R/T[i] * (CthetaSpan[i]**2./r[i])*dr - dTT)                                  # [8.140]
        rhoSpan[i-1] = rhoSpan[i] - drho
    
    return rhoSpan

def T_spanwise(T0, CthetaSpan, zSpan, cp):
    return( T0 - (CthetaSpan**2 + zSpan**2)/(2*cp) )      # [8.141]

def zSpan_station1(r, rps, r_mean, b): # Where r is a vector
    test2 = np.sqrt(r)
    return( rps.z_1m * np.sqrt(1 + 2*(b*r_mean/rps.z_1m)**2 * (1-(r**2)/(r_mean**2))) )     # [8.133]

def zSpan_station2(r, rps, r_mean, a, b): # Where r is a vector
    return( rps.z_1m * np.sqrt(1 + 2*(b*r_mean/rps.z_1m)**2 * (1-(r**2)/(r_mean**2)) - (4*a*b/(rps.z_1m**2))*np.log(r/r_mean)) )   # [8.131]

def CthetaSpan_station1(r, b): # Where r is a vector
    return( b*r )       # [8.125]

def CthetaSpan_station2(r, a, b): # Where r is a vector
    return( b*r + a/r )     # [8.126]