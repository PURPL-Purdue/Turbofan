from CoolProp.CoolProp import PropsSI
from CMYK.Object_Definitions.Base_Objects import ComponentBase
from pyfluids import Mixture, FluidsList, Input
from Python.Combustor.CEA import CEA_Wrap as CEA
from CMYK.Run.helper_functions import Secant_Method


class Burner(ComponentBase):

    def __init__(self, name):
        super().__init__(name, 'FLOWPATH')

        # INLET AND EXIT FLOWS --------------------------------
        self.FlowIn  = None
        self.FlowOut = None

        # INLET AND EXIT GEOMETRY INTERFACES ------------------
        self.GeoIn  = None
        self.GeoOut = None

        # COMPONENT PROPERTIES --------------------------------
        self.eta = None
        self.LHV = None
        self.FAR = None
        self.T04 = None
        self.pr = None

        self.Wfactor = None
        self.Wstream = None

    def Get_Mixtures(fuel: str): #-> tuple[ceaMixture, ceaMixture, list]:
        if fuel == 'Jet-A':
            fuel_cea_name = 'Jet-A(L)'
        else:
            raise RuntimeError(f"Fuel '{fuel}' not supported. Please check spelling or use a different fuel.")
        
        reactant_names = [fuel_cea_name, 'Air']
        #product_ceaMixture = ceaMixture(reactant_names, products_from_reactants = True)
        #reactant_ceaMixture = ceaMixture(reactant_names)

        return reactant_names

    def config(self) -> None:
        cfg = self.cfg[self.name]
        super()._set_Wfactor()

        self.eta = cfg['eta']
        self.LHV = cfg['LHV']
        self.pr = cfg['Pr_Des']
        self.T04 = self.cfg['CYCLE']['T0_4']


    #-----------------------------------------------------
    #                   CMYK Methods
    #-----------------------------------------------------

    def far_to_phi(self, FAR, FAR_stoich):
        return FAR / FAR_stoich

    def phi_to_far(self, phi, FAR_stoich):
        return phi * FAR_stoich

    def Run_CEA(self, FAR):
            """Run CEA and return the species list, pressure, and temperature"""

            FAR_stoich = 0.068 # Stoichiometric FAR for Jet-A and Air

            phi = self.far_to_phi(FAR, FAR_stoich)
    
            oxid = CEA.Oxidizer(name = "Air", temp = self.FlowIn.T0, wt = 100) #Oxidizer Specs
            fuel = CEA.Fuel(name = "Jet-A(L)", temp = 300, wt = 100) #Fuel Specs
    
            problem = CEA.HPProblem(pressure = (self.FlowIn.P0 / 100), massf = True, pressure_units = "bar")
            problem.set_phi(phi)
            data = problem.run(fuel, oxid)
    
            spec = [] # species list
            masses = [] # mass fraction list
    
            #create a list of the species and their corresponding mass fractions
            for element in sorted(data.prod_c):
                spec.append(element)
                masses.append(data.prod_c[element])
    
            # zip the list of elements and their corresponding mass fractions, sort them in descending order of mass fraction, and return the sorted list along with pressure and temperature
            spec_pairs = sorted(zip(masses, spec), reverse = True)
            pres = data.p
            temp = data.t
    
            return spec_pairs, pres, temp

    def CYAN(self):
        """Refer to CycleAnalysis.md for explanation of the math"""
        # PREPARING REQUIRED VALUES ---------------------
        h01 = self.FlowIn.h0
        P01 = self.FlowIn.P0
        eta = self.eta
        pr = self.pr
        LHV = self.LHV

        # T04 -------------------------------------------
        T02 = self.T04

        # P04 CALCULATION -------------------------------
        P02 = pr * P01

        # FAR CALCULATION -------------------------------
        h02 = PropsSI('HMASS', 'T', T02, 'P', P02, self.FlowIn.WF)      # TODO: Start from here, replacing working fluid with post-combustion mixture
        self.FAR = FAR = (h02 - h01) / (eta * LHV - h02)
        print(FAR)
        self.Wfactor += FAR

        def Residual(FAR):
            """Returns difference between CEA-predicted T04 and target T04"""
            _, _, T_cea = self.Run_CEA(FAR)
            return T_cea - T02
    
        # initial guesses for FAR - bracket a reasonable range
        FAR_guess0 = 0.005
        FAR_guess1 = 0.05

        self.FAR = FAR = Secant_Method(Residual, FAR_guess0, FAR_guess1, 1e-6, 50)

        print(FAR)

        # get final species/pressure/temp at converged FAR
        spec_pairs, P02, T02 = self.Run_CEA(self.FAR)
        print(P02, T02)

        # SET EXIT FLOW ---------------------------------
        self.FlowOut.setFlow(
            T0 = T02, P0 = (P02 * 100), FAR = FAR,
            Wfactor = self.Wfactor, Wstream = self.Wstream
        )