#--------------------------------------------------------------------------------------#

# def enthalpy_calc(t,A,B,C,D,E,MW):
#     cp = (A+B*(t)+C*(t^2)+D*(t^3)+E*(t^-2))/MW
#     return(cp)

# def v4_calc(mr1,mr2,t3,t4,cp1,cp2,cpf,vpz,vair):
#     v_fin = math.sqrt(2*((mr1*(cp1*t3+(vpz**2)/2))+(mr2*(cp2*t3+(vair**2)/2)) + cpf*t4))
#     return (v_fin)

# pres3 = data.p #pressure (bar)

# m_r_pz = .14 #mass flow ratio of primary zone (kg/s)
# m_r_air = .86 #mass flow ratio of air zone (kg/s)
# m_d_fin = m_r_pz + m_r_air #total mass flow, mass flow exit (kg/s)

# temp3 = 900 #Temperature at Zone 3 (K)
# temp4 = 1300 #Temperature at Zone 4 (K)

# mw_O2 = 31.998
# mw_N2 = 28.0134
# cp_N2 = enthalpy_calc(temp3,19.50583,19.88705,-8.598535,1.369784,.527601,mw_N2) #constant pressure enthalpy for primary zone (kJ/kg)
# cp_O2 = enthalpy_calc(temp3,30.03235,8.772972,-3.988133,0.788313,-.741599,mw_O2) #constant pressure enthalpy for air zone (kJ/kg)
# cp_dod = 376/170.3348
# cp_pz = 21.83675*cp_O2+71.87998*cp_N2+6.28327*cp_dod
# cp_air = .233*cp_O2 + (1-.233)*cp_N2
# cp_fin = data.cp #constant pressure enthalpy for exit (kJ/kg)
# temp4 = data.t

# vel_pz = .4/(343)
# vel_air = .4/(343)

# v4 = v4_calc(m_r_pz,m_r_air,temp3,temp4,cp_pz,cp_air,cp_fin,vel_pz,vel_air)

# print(v4)