#ATTEMPT 1: CEA CODE

#from Reference import REF_structs
import CEA_Wrap as CEA
from pyfluids import FluidsList,Mixture,Input

#test variables
T03 = 896.57321 #temp station 3 (K)
P03 = 2238.73 #pressure station 3 (kPa)
phi = 1 # fuel/oxid equivaluence ratio

fuel = CEA.Fuel(name = "Jet-A(L)", temp = 300, wt=100) #Fuel Specs
oxid = CEA.Oxidizer(name = "Air",temp = T03,wt=100) #Oxidizer Specs

def CEA_run(P03, T03, phi, fuel, oxid): #code to run CEA
    
    #run CEA
    problem = CEA.HPProblem(pressure=(P03/100),massf= True,pressure_units= "bar") #Setup CEA
    problem.set_phi(phi) #Define phi

    data = problem.run(fuel,oxid) #extract data

    #create list of output species and mass fractions
    spec = []
    values = []

    for element in sorted(data.prod_c):
        spec.append(element)
        values.append(data.prod_c[element])

    #merge the two list and sort by mass fraction (highest to lowest), keeping the element name together
    pairs = sorted(zip(values,spec),reverse = True)

    #use data.variable for data extraction- all can be found at the dude's website
    # potential variable replacements:
    # p - pressure (bar)
    # t - temperature
    # h - enthalpy
    # cp - specific heat capacity
    # mw - molecular weight of products
    # son- sonic velocity
    # prod_c- list of products

    # Inputs:
    # P03- Pressure at station 3 (kPa)
    # T03- Temperature at station 3 (K)
    # phi- fuel/air equivalence ratio (<1 is lean, >1 is rich)
    # fuel- fuel name (string unless custom)
    # ox- oxidizer name (string unless custom)

    pres = data.p #pressure output from CEA (bar)
    temp = data.t #temperature output from CEA (K)

    return(pairs,pres,temp) #return the match pairs, pressure, and temperature



# Common combustion species available in CoolProp- made by chatGPT (I'm lazy)
# basically just a big library to covert compounds from CEA into names use by coolprop
coolprop_species = {
    # Major oxidizer species
    "N2": "Nitrogen",
    "O2": "Oxygen",
    "Ar": "Argon",

    # Fuel and combustion products
    "H2O": "Water",
    "CO2": "CarbonDioxide",
    "CO": "CarbonMonoxide",
    "H2": "Hydrogen",

    # Hydrocarbon fuels
    "CH4": "Methane",
    "C2H6": "Ethane",
    "C2H4": "Ethylene",
    "C3H8": "nPropane",
    "C3H6": "Propylene",
    "C4H10": "nButane",
    "C4H8": "Butene",

    # Oxygenated fuels
    "CH3OH": "Methanol",
    "C2H5OH": "Ethanol",
    "CH3OCH3": "DimethylEther",

    # Nitrogen-containing species
    "NH3": "Ammonia",

    # Sulfur species
    "SO2": "SulfurDioxide",
    "H2S": "HydrogenSulfide",

    # Halogens
    "HCl": "HydrogenChloride",
    "Cl2": "Chlorine",
    "F2": "Fluorine",

    # Noble gases
    "He": "Helium",
    "Ne": "Neon",
    "Kr": "Krypton",
    "Xe": "Xenon",
}



def Cool_prop(pairs,pres,temp,coolprop_species): #run coolprop
    
    #converts products to be useable in coolflow
    cool = []
    count = 0

    for mf,spec in pairs: #this keeps the top 5 products and adds them to a list
        if count < 5:
            if spec in coolprop_species: #only uses species in coolprop (no NO, OH, C(cr), H, O)
                cool.append((mf,coolprop_species[spec]))
                count += 1

    # now this section is where it get questionable. Basically coolprop mass fractions have to add up 
    # to exactly 100, and it made it much easier to convert the fab 5 to integers. Maybe floats can be 
    # used, but i was not able to figure it out
    mass_per = []
    round_mass_per = []
    species = []

    for masf,speci in cool: #makes separate list for products, and rounded and unrounded mass percents
        round_mass_per.append(round(masf*100))
        mass_per.append(masf*100)
        species.append(speci)

    error = [(per-round(per)) for per in mass_per] #calculate error from rounding

    #if sum of mass fractions is under 100, 1 is added to the most rounded down number till it is 100
    while sum(round_mass_per) < 100: 
        max_error = error.index(max(error))
        error[max_error] = 0
        round_mass_per[max_error] +=1

    #if sum of mass fractions is over 100, 1 is subtract to the most rounded down number till it is 100
    while sum(round_mass_per) > 100:
        min_error = error.index(min(error))
        error[min_error] = 0
        round_mass_per[min_error] -= 1

    #converts all products from CEA into compounds usable for coolprop
    fluid = []

    for specy in species:
        fluid.append(FluidsList(specy))

    pressure = pres*1e5 #bar to Pa
    temperature = temp - 273 #K to C

    #all of that for one stupid line of code
    mixture = Mixture(fluid,round_mass_per).with_state(Input.pressure((pressure)),Input.temperature((temperature)))
    return(mixture)

pairs,pres,temp = CEA_run(P03, T03, phi, fuel, oxid)

mix = Cool_prop(pairs,pres,temp,coolprop_species)
