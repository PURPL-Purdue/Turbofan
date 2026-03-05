import CEA_Wrap as CEA

#run CEA
fuel = CEA.Fuel(name = "Jet-A(L)", temp = 300, wt=100) #Fuel Specs
oxid = CEA.Oxidizer(name = "Air",temp = 900,wt=100) #Oxidizer Specs

problem = CEA.HPProblem(pressure=5,massf= True,pressure_units= "bar") #Setup CEA
problem.set_phi(1) #Define phi

data = problem.run(fuel,oxid) #extract data

#use data.variable for data extraction- all can be found at the dude's website
# potential variable replacements:
# p - pressure
# t - temperature
# h - enthalpy
# cp - specific heat capacity
# mw - molecular weight of products
# son- sonic velocity
