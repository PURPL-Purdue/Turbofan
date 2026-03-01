import numpy as np
import REF_structs
import REF_AEQ as AEQ
import Plotting as plot

def thermoCalcs(params):
    eta    = params.eta                      # Isetronpic efficiencies
    gamma  = params.gamma                    # Specific heat ratios
    Pr     = params.Pr                       # Design pressure ratios
    T_0    = params.T_0                      # Ambient temp
    P_0    = params.P_0                      # Ambient pressure
    M_f    = params.M_f                      # Flight mach number
    Ra     = params.Ra                       # Gas constant of air
    Rp     = params.Rp                       # Gas constant of combustion products
    QR     = params.QR                       # Heat of reaction for combustion
    bypass = params.bypass                   # Bypass ratio
    combustion_temp = params.combustion_temp # Combustion temperature

    # lmao who cares about station 1 am i right (???)
    # ======== Station 1.5: Diffuser Outlet /Fan Inlet ========
    T0_15 = T_0/AEQ.T_T0(gamma.a, M_f)
    P0_15 = P_0*(1 + eta.d*(T0_15/T_0 - 1))**(gamma.d/(gamma.d-1))

    # ======== Station 2: Fan Outlet/LP Compressor Inlet ========
    Cp_f = (Ra*gamma.f)/(gamma.f-1)     # Specific heat of fan

    T0_2 = T0_15*(1 + 1/eta.f*(Pr.f**((gamma.f-1)/gamma.f)-1))
    P0_2 = P0_15*Pr.f

    # ======== Station 2.5: LP Compressor Outlet/HP Compressor Inlet ========
    Cp_cLP = (Ra*gamma.cLP)/(gamma.cLP-1)     # Specific heat of compressor

    T0_25 = T0_2*(1 + 1/eta.cLP*(Pr.cLP**((gamma.cLP-1)/gamma.cLP)-1))
    P0_25 = P0_2*Pr.cLP

    # ======== Station 3: HP Compressor Outlet/Burner Inlet ========
    Cp_cHP = (Ra*gamma.cHP)/(gamma.cHP-1)     # Specific heat of compressor

    T0_3 = T0_25*(1 + 1/eta.cHP*(Pr.cHP**((gamma.cHP-1)/gamma.cHP)-1))
    P0_3 = P0_25*Pr.cHP

    # ======== Station 4: Burner Outlet/HP Turbine Inlet ========
    Cp_b = (Rp*gamma.b)/(gamma.b-1)     # Specific heat of burner

    T0_4 = combustion_temp
    P0_4 = P0_3*Pr.b

    fr = (T0_4/T0_3 - 1)/((eta.b*QR)/(Cp_b*T0_3)-T0_4/T0_3)   # Fuel-air ratio

    # ======== Station 4.5: HP Turbine Outlet/LP Turbine Inlet ========
    Cp_tHP = (Rp*gamma.tHP)/(gamma.tHP-1)     # Specific heat of turbine

    T0_45 = ((1+fr)*T0_4*Cp_tHP - Cp_cHP*(T0_3-T0_25)) / ((1+fr)*Cp_tHP)
    # T0_45 = 1/(1+fr) * Cp_cHP/Cp_tHP * (T0_25 - T0_3) + T0_4
    P0_45 = P0_4*(1 - 1/eta.tHP*(1 - T0_45/T0_4))**(gamma.tHP/(gamma.tHP-1))

    # ======== Station 5: LP Turbine Outlet/Nozzle Inlet ========
    Cp_tLP = (Rp*gamma.tLP)/(gamma.tLP-1)     # Specific heat of turbine

    T0_5 = ((1+fr)*T0_45*Cp_tLP - Cp_cLP*(T0_25-T0_2) - bypass*Cp_f*(T0_2-T0_15)) / ((1+fr)*Cp_tLP)
    # T0_5 = (Cp_cLP*(T0_25-T0_3) + bypass*Cp_f*(T0_15-T0_2))/((1+fr)*Cp_tLP) + T0_45
    P0_5 = P0_45*(1 - 1/eta.tLP*(1 - T0_5/T0_45))**(gamma.tLP/(gamma.tLP-1))
    
    # ======== Station 6: Afterburner (there is none lmao) ========
    T0_6 = T0_5
    P0_6 = P0_5

    # ======== Station 7: Nozzle Outlet ========
    T0_7 = T0_6
    P0_7 = P0_6

    # ======== Station 8: Aft Ambient ========
    T_8 = T_0
    P_8 = P_0

    # ======== Nozzle Exit Velocities ========
    u_ec = np.sqrt(2*eta.n *(gamma.n /(gamma.n -1))*Rp*T0_7*(1 - (P_8/P0_7)**((gamma.n -1)/gamma.n )))
    u_ef = np.sqrt(2*eta.fn*(gamma.fn/(gamma.fn-1))*Ra*T0_2*(1 - (P_8/P0_2)**((gamma.fn-1)/gamma.fn)))

    # ======== Performance Metrics ========
    u_a = M_f * np.sqrt(gamma.a*Ra*T_0)
    
    ST = (1+fr)*u_ec + bypass*u_ef - (1+bypass)*u_a     # Specific Thrust
    ST_core = (1+fr)*u_ec - u_a 
    ST_bypass = bypass*u_ef - bypass*u_a

    TSFC = fr/ST                                        # Thrust Specific Fuel Consumption
    eta_p  = ST*u_a / ((1+fr)*((u_ec**2)/2) + bypass*((u_ef**2)/2) - (1+bypass)*((u_a**2)/2))     # Propulsive Efficiency
    eta_th = ((1+fr)*((u_ec**2)/2) + bypass*((u_ef**2)/2) - (1+bypass)*((u_a**2)/2)) / (fr*QR)    # Thermal Efficiency
    eta_0  = eta_p*eta_th

    T0P0 = REF_structs.StationThermo(
                        REF_structs.StationTnP(T_0,   P_0),
                        REF_structs.StationTnP(T0_15, P0_15),
                        REF_structs.StationTnP(T0_2,  P0_2),
                        REF_structs.StationTnP(T0_25, P0_25),
                        REF_structs.StationTnP(T0_3,  P0_3),
                        REF_structs.StationTnP(T0_4,  P0_4),
                        REF_structs.StationTnP(T0_45, P0_45),
                        REF_structs.StationTnP(T0_5,  P0_5),
                        REF_structs.StationTnP(T0_6,  P0_6),
                        REF_structs.StationTnP(T0_7,  P0_7),
                        REF_structs.StationTnP(T_8,  P_8),
                        )
    
    Cps = REF_structs.ByComponent(
        f= Cp_f,
        cLP = Cp_cLP,
        cHP = Cp_cHP,
        b= Cp_b,
        tHP = Cp_tHP,
        tLP = Cp_tLP
    )

    thrust_target = 2500*4.44822
    m_dot_core = thrust_target/ST
    m_dot_bypass = m_dot_core*bypass
    m_dot_total = m_dot_core + m_dot_bypass
    total_thrust = m_dot_core*ST / 4.44822
    core_thrust = m_dot_core * ST_core / 4.44822
    bypass_thrust = m_dot_core * ST_bypass / 4.44822

    cycle_OUT = REF_structs.Cycle_OUT(
        T0P0,
        Cps,
        ST,
        TSFC,
        total_thrust,
        core_thrust,
        bypass_thrust,
        eta_p,
        eta_th,
        eta_0,
        m_dot_core,
        m_dot_bypass,
        m_dot_total,
        u_ec,
        u_ef
    )
    
    return cycle_OUT