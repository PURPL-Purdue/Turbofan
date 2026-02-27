## required inputs
t3 = 900 # temperature from compressor (K)
t4 = 1300 # desired temperature to turbine (K)
t_flame = 2500 # flame temperature (K)
mDotAir = 8 # mass flow of air (kg/s)
mDotFuel = 0.1 # mass flow of fuel (kg/s)

pzd = 0 # fraction of mass flow to the primary zone (unitless)
szd = 0 # fraction of mass flow to the secondary zone (unitless)
dzd = 0 # fraction of mass flow to the dilution zone (unitless)
inc = 0.01 # increment for iterating through the fractions



def calc_outlet_temp(pzd, szd, dzd, mDotAir, mDotFuel, t3, t4, t_flame):
    # Calculate the mass flow rates for each zone
    mDotPrimary = pzd * mDotAir
    mDotSecondary = szd * mDotAir
    mDotDilution = dzd * mDotAir

    # Calculate the total mass flow to the turbine
    mDotTotal = mDotAir + mDotFuel

    # Calculate the outlet temperature using energy balance
    tOutlet = ((mDotPrimary + mDotFuel) * t_flame + mDotSecondary * t3 + mDotDilution * t3) / mDotTotal

    return tOutlet



while pzd <= 1:
    szd = 1 - pzd

    while szd >= 0:
        dzd = 1 - pzd - szd
        outlet_t = calc_outlet_temp(pzd, szd, dzd, mDotAir, mDotFuel, t3, t4, t_flame)

        if outlet_t >= t4: # outputs when desired temp is reached
            pzd -= inc
            szd = 1 - pzd
            dzd = 1 - pzd - szd
            print(f" Outlet temperature: {temp_outlet:.2f}, pzd {pzd :.4f}, szd: {szd:.4f}, dzd: {dzd:.4f}")
            pzd = 2
            szd = -1

        temp_outlet = outlet_t
        szd -= inc

    pzd += inc