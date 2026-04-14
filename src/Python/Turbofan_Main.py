import Component_Sizing
from Reference import REF_structs
from Cycle     import Station_Thermo
from Output    import Print_Results
from Output    import Plotting

# Initializing dataclasses for component efficiencies, specific heat ratios, and pressure ratios

TF = REF_structs.TF()

TF.cycle.IN.eta = REF_structs.ByComponent(
    d   = 0.94, # Diffuser
    f   = 0.85, # Fan
    fn  = 0.98, # Fan Nozzle
    cLP = 0.75, # LP Compressor
    cHP = 0.75, # HP Compressor
    b   = 0.95, # Burner
    tHP = 0.90, # HP Turbime
    tLP = 0.90, # LP Turbine
    n   = 0.98  # Nozzle
)
TF.cycle.IN.gamma = REF_structs.ByComponent(
    a   = 1.4,  # Ambient
    d   = 1.4,  # Diffuser
    f   = 1.4,  # Fan
    fn  = 1.4,  # Fan Nozzle
    cLP = 1.4,  # LP Compressor
    cHP = 1.4,  # HP Compressor
    b   = 1.3,  # Burner
    tHP = 1.32, # HP Turbine
    tLP = 1.32, # LP Turbine
    n   = 1.34  # Nozzle
)
TF.cycle.IN.Pr = REF_structs.ByComponent(
    f   = 1.7,          # Fan
    cLP = 2.6,          # LP Compressor
    cHP = 5,            # HP Compressor
    b   = 1,            # Burner
)

# ======== Ambient Conditions and General Engine Parameters ========
TF.cycle.IN = REF_structs.Cycle_IN(
    TF.cycle.IN.eta,    # eta               Efficiencies                       | nondimensional
    TF.cycle.IN.gamma,  # gamma             Specific heat ratios               | nondimensional
    TF.cycle.IN.Pr,     # Pr                Design pressure ratios             | nondimensional
    298,                # T_0               Freestream/ambient temperature     | K
    101300,             # P_0               Freestream pressure                | Pa
    0.0,                # M_f               Freestream/flight Mach number      | nondimensional
    287,                # Ra                Air gas constant                   | TODO
    287,                # Rp                Combustion product gas constsant   | TODO
    45000000,           # QR                Heat of reaction of fuel           | TODO
    2.89,               # Bypass            Bypass Ratio                       | nondimensional
    1300                # combustion_temp   T0_4, turbine inlet temp           | K
)
TF.cycle.OUT = Station_Thermo.thermoCalcs(TF.cycle.IN)

TF.compressor.LP.IN = REF_structs.Compressor_IN(
    TF.cycle.IN.gamma.cLP,      # gamma             Specific heat ratio                         | nondimensional
    TF.cycle.OUT.Cps.cLP,       # Cp_cLP            Specific heat capacity at constant volume   | TODO
    TF.cycle.OUT.T0P0.S2.T0,    # T0_1              Compressor inlet face total temperature     | Pa
    TF.cycle.OUT.T0P0.S2.P0,    # P0_1              Compressor inlet face total pressure        | K
    TF.cycle.IN.Pr.cLP,         # Pr                Design pressure ratio                       | nondimensional
    0.99,                       # e_c               Polytropic Efficiency                       | nondimensional
    0.6,                        # httrr             Hub-to-tip radius ratio                     | nondimensional
    0.72,                       # deHaller          De Haller's Criterion value                 | nondimensional
    300000,                     # min_Re            Minimum Reynold's number for blade sizing   | nondimensional
    1.46e-5,                    # mu_kin            Kinematic viscosity                         | TODO
    30,                         # alpha_1m          Inlet absolute flow angle                   | degrees       
    0.45,                       # Mz_1m             Inlet axial mach number                     | nondimensional
    0.95,                       # M_tip_inlet_max   Inlet rotor max allowable tip Mach number   | m/s
    TF.cycle.OUT.m_dot_core     # m_dot_core        Core mass flow rate                         | kg/s
)

TF.compressor.LP.OUT = Component_Sizing.Axial_Compressor_Sizing(TF.compressor.LP.IN)

TF.turbine.LP.IN = REF_structs.Turbine_IN(
    TF.cycle.OUT.m_dot_core,        # m_dot_t           Turbine total mass flow TODO: add in fuel mass flow | kg/s
    TF.cycle.OUT.m_dot_core,        # m_dot_c           Compressor mass flow                                | kg/s
    TF.compressor.LP.OUT.RPM,       # rpm               RPM                                                 | RPM

    TF.cycle.OUT.T0P0.S2.T0,        # T0_2comp          Compressor inlet total temp                         | K
    TF.cycle.OUT.T0P0.S25.T0,       # T0_3comp          Compressor outlet total temp                        | K
    TF.cycle.OUT.T0P0.S45.T0,       # T0_4m             Turbine inlet total temperature                     | K
    TF.cycle.OUT.T0P0.S45.P0,       # P0_4m             Turbine inlet total pressure                        | Pa 

    TF.compressor.LP.OUT.r_mean_1,  # r_mean_c          Comrpessor pitchline radius                         | m

    # For now, while we have uncooled turbine and ep = 0, these three values don't matter
    None,                           # m_dot_cool        Cooling air bleedoff mass flow                      | kg/s
    704,                            # T0_cool           Cooling air temperature                             | K
    None,                           # P0_cool           Cooling air pressure                                | Pa

    # I actually forget why these three numbers are just never used
    None,                           # M_a               Ambient Mach number                                 | nondimensional
    None,                           # P0_0m             Ambient total pressure                              | Pa
    None,                           # T0_0m             Ambient temperature                                 | K

    TF.cycle.OUT.Cps.cLP,           # Cp_c              Compressor specific heat at constant pressure       | J/kg*K
    TF.cycle.OUT.Cps.tLP,           # Cp_t              Turbine specific heat at constant pressure          | J/kg*K
    TF.cycle.IN.gamma.cLP,          # gamma_c           Comrpessor specific heat ratio                      | nondimensional
    TF.cycle.IN.gamma.tLP,          # gamma_t           Turbine specific heat ratio                         | nondimensional

    0.995,                          # eta_mech          Mechanical efficiencicy                             | nondimensional
    0.0,                            # ep                Cooling mass flow rate fraction                     | in decimal form

    # Fan Stuff
    TF.cycle.OUT.m_dot_total,       # m_dot_f           Fan (total) mass flow rate                          | J/kg*K
    TF.cycle.OUT.Cps.f,             # Cp_f              Fan specific heat at constant pressure              | J/kg*K
    TF.cycle.OUT.T0P0.S15.T0,       # T0_15             Fan inlet total temperature                         | K

    # First stage design decisions
    0.0,                            # alpha_1m          alpha_1                                             | radians
    60,                             # alpha_2m          alpha_2                                             | radians
    1.1,                            # Mc_2m             First stator nozzle Mach number, choked flow        | nondimensional
    0.8,                            # Mw_3Rm            First rotor relative exit Mach number               | nondimensional

    # Multistage design decisions
    0.964,                          # Mc_2m_default     Subsequent stator nozzle Mach number, keep <1       | nondimensional
    0.85                            # Mw_3Rm_default    Subsequent rotor relative exit Mach number          | nondimensional
)

TF.turbine.LP.OUT = Component_Sizing.Turbine_Sizing(TF.turbine.LP.IN)

TF.nozzle.IN = REF_structs.Nozzle_IN(
    TF.cycle.OUT.m_dot_core,        # mclear_dot_c           Core total mass flow TODO: add in fuel mass flow    | kg/s
    TF.cycle.OUT.m_dot_bypass,      # m_dot_b           Bypass mass flow                                    | kg/s

    TF.cycle.OUT.T0P0.S5.T0,        # T0_5              Turbine outlet total temperature                    | K
    TF.cycle.OUT.T0P0.S5.P0,        # P0_5              Turbine outlet total pressure                       | Pa 
    TF.cycle.OUT.T0P0.S15.T0,       # T0_15             Bypass duct total temperature                       | K
    TF.cycle.OUT.T0P0.S15.P0,       # P0_15             Bypass duct total pressure                          | Pa 
    TF.cycle.IN.T_0,                # P0_0m             Ambient total pressure                              | Pa
    TF.cycle.IN.P_0,                # T0_0m             Ambient total temperature                           | K

    TF.cycle.IN.gamma.n,            # gamma_n           Nozzle specific heat ratio                          | nondimensional
    TF.cycle.IN.gamma.fn,           # gamma_fn          Fan nozzle specific heat ratio                      | nondimensional
    TF.cycle.IN.eta.n,              # eta_n             Nozzle efficiency                                   | nondimensional
    TF.cycle.IN.eta.fn,             # eta_fn            Fan nozzle efficiency                               | nondimensional
)

TF.nozzle.OUT = Component_Sizing.Nozzle_Sizing(TF.nozzle.IN)

Print_Results.write(TF)
#Plotting.plot(TF)