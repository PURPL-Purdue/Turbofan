# Cycle Analysis Documentation
The following documentation covers what cycle analysis is, what its role and usage is within the CMYK solver, and goes into the math behind individual components

## What is Cycle Analysis?
Cycle analysis refers to the thermodynamic analysis of the engine cycle. Most often, in the context of air-breathing propulsion, we focus on the Brayton cycle, which is a thermodynamic cycle employed by most conventional turbojets and turbofans. Other modified-Brayton cycle engines are being developed, but that is outside the scope of this project. There are two key desired outcomes of a cycle analysis. The first is the complete definition of all inter-component thermodynamic states. At a basic level, this means calculating the temperatures and pressures at each location between engine components i.e. between the LPC and the HPC, between the burner and the HPT, etc. The second goal of a cycle analysis is to predict the performance of the engine in terms of thrust, specific thrust, thrust-specific fuel consumption, etc. These performance parameters let us know if the engine is able to do what we want it to do.

## Cycle Analysis Implementation in CMYK
Because CMYK is object-oriented, each component object handles its own portion of the cycle analysis. Excluding the Ambient class, each component class has at least one ```FlowIn``` and one ```FlowOut``` object, each referencing a ```Flow``` object. Each component class also has a ```CYAN()``` method, (CYAN for CYcle ANalysis) which takes in no parameters. When the engine-level ```CYAN()``` method of the ```Engine``` object is called, the component-level ```CYAN()``` method of each individual component in the flowpath is called sequentially, performing the cycle analysis of the whole engine. The sole purpose of the component-level ```CYAN()``` methods is to calculate and set the properties of its ```FlowOut``` object(s) based on the values found in its ```FlowIn``` object(s). To facilitate the transfer of information between components, the engine-level interface() method is used to link the ```Flow``` objects between components. Shown below is a wonderful ASCII art diagram showing how sequential components reference the same ```Flow``` object. Since python variables are pointers, both ```Component1.FlowOut``` and ```Component2.FlowIn``` point to the exact same ```Flow``` object in memory. That way, when ```Component1``` updates ```Component1.FlowOut```, ```Component2``` is immediately able to access the new values in ```Component2.FlowIn```


```aiignore
┌────────────────────────────────┐      ┌────────────────────────────────┐
│  Component1 Object             │      │             Component2 Object  │
│     (upstream)                 │      │               (downstream)     │
│                                │      │                                │
│  self.FlowIn     self.FlowOut  │      │  self.FlowIn     self.FlowOut  │
└────────┬───────────────┬───────┘      └────────┬───────────────┬───────┘
         │               │    ┌─────────────┐    │               │
   ···───┘               └────│ Flow Object ├────┘               └────···
                              └─────────────┘
```
---
## Component Math

### Nomenclature

**IMPORTANT NOTE**: For all components, the numbering scheme is the same, with the subscript $_{1}$ denoting inlet conditions and the subscript $_{2}$ denoting exit conditions. This goes against the standard numbering convention of air-breathing engines, but in the interest of emphasizing the decentralized nature of the ```CYAN()``` methods, this "local" numbering scheme has been adopted.

---
### Inlet

#### Assumptions
- Steady state ($\frac{dE}{dt}=0$)
- Adiabatic ($\dot{Q}=0$)
- Passive ($\dot{W}=0$)
- Neglect gravity

#### Inputs
- Isentropic Efficiency ($\eta$)

#### Exit Total Temperature Calculation
Using the adiabatic assumption, $T_{0,out} = T_{0,in}$

#### Exit Total Pressure Calculation
The definition of isentropic efficiency for an inlet/diffuser yields
$$\eta=\frac{h_{02s}-h_1}{h_{02}-h_1}$$
Of these values, $\eta$ is an input and is known, and $h_1$ is known from the upstream flow. Note that static enthalpy is known because the inlet always follow an ambient object, where static conditions are known. This is not necessarily true later in the cycle analysis, as once we enter the engine, Mach number becomes unknown and therefore only total quantities are tracked. Using the first law of thermodynamics on an open system and applying our assumptions and conservation of mass, we get
$$ \begin{aligned} \frac{dE}{dt} &= \dot{Q} - \dot{W} + \dot{m}_1 h_{01} - \dot{m}_2 h_{02} \\ h_{01} &= h_{02} \end{aligned} $$
Because $h_{01}$ is known from the upstream flow, we now know all terms in the definition of $\eta$ except for $h_{02s}$, which we can now solve for. We also know $s_{2s}=s_{1}$, so we can query ```CoolProp``` using enthalpy and entropy to get $P_{02s}$. By definition, $P_{02}=P_{02s}$, so we have successfully determined $P_{02}$

---
### Compressors (Fan, LPC, HPC)
The cycle analysis does not distinguish between the fan, the axial LPC, and the radial LPC. All it cares about is the fact that adiabatic compression is happening, so the cycle analyses for all the components are the same.

#### Assumptions
- Steady state ($\frac{dE}{dt}=0$)
- Adiabatic ($\dot{Q}=0$)
- Active ($\dot{W}\ne0$)
- Neglect gravity

#### Inputs
- Isentropic Efficiency ($\eta$)
- Design pressure ratio ($\pi$)

#### Exit Total Pressure Calculation
Since a design pressure ratio is specified, we simply multiply the inlet total pressure by the design pressure ratio to obtain design exit total pressure i.e. $P_{02} = \pi P_{01}$

#### Exit Total Temperature Calculation
We know that $s_{2s}=s_1$ and $P_{02s}=P_{02}$, so we can query ```CoolProp``` with total pressure and entropy to obtain total enthalpy $h_{02s}$. Looking at the definition of compressor isentropic efficiency,
$$\eta=\frac{h_{02s}-h_{01}}{h_{02}-h_{01}}$$
we can see that we can now solve for $h_{02}$, as $\eta$ is a known input and $h_{01}$ is known from the upstream flow. Finally, we can query ```CoolProp``` once more with $h_{02}$ and $P_{02}$ to obtain $T_{02}$

---
### Burner
In addition to calculating the outlet total pressure and temperature, the burner cycle analysis also calculates the fuel-to-air ratio. This is an important parameter to calculate, as it affects mass conservation for the rest of the hot section of the engine.

#### Assumptions
- Steady state ($\frac{dE}{dt}=0$)
- Diabatic ($\dot{Q}\ne0$)
- Passive ($\dot{W}=0$)
- Neglect gravity

#### Inputs
- Isentropic Efficiency ($\eta$)
- Design pressure ratio ($\pi$)
- Burner exit total temperature ($T_{04}$ in engine-level station numbering, $T_{02}$ for the CYAN() method)
- Lower heating value of the fuel ($LHV$)

#### Exit Total Pressure Calculation
Since a design pressure ratio is specified, we simply multiply the inlet total pressure by the design pressure ratio to obtain design exit total pressure i.e. $P_{02} = \pi P_{01}$.

#### Exit Total Temperature
Exit total temperature is a given input.

#### Fuel-to-Air Ratio Calculation
Starting with the first law energy balance and simplifying using the assumptions and mass conservation, we obtain
$$ \begin{aligned}
\frac{dE}{dt} &= \dot{Q} - \dot{W} + \dot{m}_1 h_{01} + \dot{m}_f h_f - \dot{m}_2 h_{02} \\ \dot{m}_f \eta LHV &= (\dot{m}_1 + \dot{m}_f)h_{02} - \dot{m}_1 h_{01}
\end{aligned} $$
Dividing everything by $\dot{m}_1$ and simplifying yields
$$ \begin{aligned}
f \eta LHV &= (1 + f)h_{02} - h_{01} \\
f \eta LHV &= h_{02} + fh_{02} - h_{01} \\
f (\eta LHV - h_{02}) &= h_{02} - h_{01} \\
f &= \frac{h_{02} - h_{01}}{\eta LHV - h_{02}}
\end{aligned} $$
From the upstream flow, $h_{01}$ is known. $P_{02}$ and $T_{02}$ are both known at this point as well, so we can query ```CoolProp``` for $h_{02}$. Thus, $f$ can be calculated.

---
### Turbines (HPT, LPC)
The cycle analysis does not distinguish between axial and radial turbines, all it cares about is the fact that adiabatic expansion occurs. Additionally, the current furbofan design does not feature a radial turbine, so we don't need to worry about it at all. This is just left as a note to the reader should radial turbines be considered in the future.

#### Assumptions
- Steady state ($\frac{dE}{dt}=0$)
- Adiabatic ($\dot{Q}=0$)
- Active ($\dot{W}\ne0$)
- Neglect gravity

#### Inputs
- Isentropic Efficiency ($\eta$)

### Power Balance
The most important thing to consider when analyzing a turbine in a cycle analysis is power matching. The turbine must generate enough power to drive all other power consumers (PCs) on the same spool. In the case of our turbofan, the main PCs are the fan and LPC for the LPT, and the HPC for the HPT. To keep the class flexible for the HPT, LPT, and future configurations, the turbine cycle analysis has been designed to work for any arbitrary number of PCs attached to the same shaft.

Applying the required power balance, we see that $$-\dot{W}_t = \frac{\sum\dot{W}_{c,i}}{\eta_m}$$ where $\dot{W}_t$ refers to the power generated by the turbine, $\dot{W}_{c,i}$ refers to the power consumed/reqiured by an individual PC $i$ (again, these generally will refer to compressors), and $\eta_m$ is a mechanical efficiency factor (a property of the shaft/bearings).

For each PC $i$, the required power can be calculated as $\dot{W}_{c,i} = \zeta_i\dot{m}_{core}(h_{02,i}-h_{01,i})$ where $\dot{m}_{core}$ is the mass flow rate through the core and $\zeta_i$ is a multiplier that describes the mass flow rate through a given component relative to the core mass flow rate. In the code, $\zeta$ is named ```Wfactor```, and is an attribute of each component class. A $\zeta$ of $1$ means that the mass flow rate through that component is equal to the mass flow rate, while a component such as the fan would have a $\zeta$ value of $1+\text{Bypass}$. For components that have multiple FlowOuts such as the fan, the current turbine CYAN() implementation defaults to the FlowOut_COR core flow object to obtain exit conditions. This is an arbitrary choice, and has no effect because the exit state is the same for FlowOut_COR and FlowOut_BYP. In contrast, it is entirely possible for a component with multiple FlowIns to have differing upstream conditions, so the current implementation throws an error. No objects currently exist that have multiple upstream flows, but this note is left in case one is added in the future.

Similarly, the power generated by the turbine can be expressed as $\dot{W}_t = \zeta_t\dot{m}_{core}(h_{02,t}-h_{01,t})$

Thus, the power balance summation becomes
$$-\zeta_t\dot{m}_{core}(h_{02,t}-h_{01,t}) = \frac{\sum\zeta_i\dot{m}_{core}(h_{02,i}-h_{01,i})}{\eta_m}$$
Cancelling $\dot{m}_{core}$ from both sides yields
$$-\zeta_t(h_{02,t}-h_{01,t}) = \frac{\sum\zeta_i(h_{02,i}-h_{01,i})}{\eta_m}$$

The entire right-hand summation side of this equation is known from previous segments of the cycle analysis, and on the left-hand side, $\zeta_t$ and $h_{01,t}$ are known quantities. Thus, we isolate solve directly for $h_{02,t}$ of the turbine:

$$h_{02,t} = \frac{\sum\zeta_i(h_{02,i}-h_{01,i})}{-\zeta_t\eta_m} + h_{01,t}$$

Next, we can apply the definition of turbine adiabatic efficiency

$$\eta=\frac{h_{02}-h_{01}}{h_{02s}-h_{01}}$$

and solve for $h_{02s}$. Combining this with $s_{2s} = s_1$, we can query ```CoolProp``` with enthalpy and entropy to get $P_{02} = P_{02s}$. Finally, we can give ```CoolProp``` $P_{02}$ and $h_{02}$ to find $T_{02}$

---
### Nozzle
A note on the CMYK solver: It is possible that by the time we reach the nozzle, total pressure is less than the ambient static pressure. If this is the case, that means the engine configuration and what we want out of it are incompatible. Possible reasons could include that we didn't put enough power into the flow through the compressors, or perhaps we tried to extract too much work in the turbines. Essentially, P09 < P_amb means that we have used up more energy than we have put into the system. The nozzle ```CYAN()``` method will check for this first, and raise an error if it occurs

For the nozzle cyle analysis, we will assume that the nozzle is perfectly expanded (after all, who doen't want max thrust eh?)

#### Assumptions
- Steady state ($\frac{dE}{dt}=0$)
- Adiabatic ($\dot{Q}=0$)
- Passive ($\dot{W}=0$)
- Neglect gravity
- Perfectly expanded

#### Inputs
- Isentropic Efficiency ($\eta$)

#### Design Modes
There are a couple different ways to go about designing the nozzle, and the approach taken can be specifed by the user by setting the ```design_mode``` option in ```config.yaml```, which must be a string. The three valid options are ```PERFECTLY_EXPANDED```, ```CONVERGING_DIVERGING```, and ```CONVERGING```. First, regardless of the design mode, the solver will check to see if the flow will choke or not. To determine if the nozzle is choking or not, we compare the nozzle pressure ratio $NPR = \frac{P_{01}}{P_2}$ to the critical pressure ratio $NPR_{crit} = \left(1 + \frac{\gamma-1}{2}\right)^{\frac{-\gamma}{\gamma-1}}$. If $NPR \ge NPR_{crit}$, then the flow chokes. $P_{01}$ is known from the upstream flow condition, and $P_2$ is assumed to equal $P_{amb}$ at the exit of the nozzle


Then, the following logic is executed:
- if ```PERFECTLY_EXPANDED```: If $NPR > NPR_{crit}$, the flow chokes, and a perfectly expanded converging-diverging nozzle will be designed. If $NPR = NPR_{crit}$, the flow chokes, and a converging nozzle will be designed with a sonic exit. If $NPR < NPR_{crit}$, a converging nozzle will be designed with a subsonic exit
- ```CONVERGING_DIVERGING```: If $NPR > NPR_{crit}$, the flow chokes, and a perfectly expanded converging-diverging nozzle will be designed. Otherwise, a runtime error will be raised.
- ```CONVERGING```: If $NPR \le NPR_{crit}$, a converging nozzle will be designed. Otherwise, a runtime error will be raised.

#### ```PERFECTLY_EXPANDED```

Taking a look at the definition of nozzle isentropic efficiency (which is a known input), we get
$$\eta=\frac{h_{01}-h_2}{h_{01}-h_{2s}}$$
From the upstream flow, we know $h_{01}$, and $h_{2s}$ can be found by querying ```CoolProp``` with $P_{2s}=P_2=P_{amb}$ and $s_{2s} = s_1$. Thus, we can solve for $h_2$. Using ```CoolProp``` with $h_2$ and $P_2$ yields $T_2$

Because we are assuming that the nozzle is adiabatic, $T_{02} = T_{01}$, so we can use $T_{02}$ and $T_2$ to calculate $M_2$ and fully define the exit jet flow state.

- **Choked**: