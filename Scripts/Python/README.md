# PURPL Turbofan
The PURPL Turbofan project aims to design, manufacture, and test a 2500-lbf turbofan engine

## Code Structure and Introduction
This following section contains a brief overview of how the code for the turbofan project is structured. I do not claim this to be the best way to structure code, so if you, the reader, has any suggestions for how to better format, structure, write, and comment code, please let me know!
\- Marvel Zheng

Note: This was written on 3/1/26 and I'm guessing by now there's new stuff in the repo that I haven't mentioned here. If this README is egregiously out of date, please let me know and I can update it.

### File Hierarchy
- At the very top, we've got Turbofan_Main.py, which is the main execution file and is the only file you should actually run.
- On the next level down we've got Station_Thermo, Component_Sizing, Print_Results, and Plotting. These are the only files that are directly called from Turbofan_Main. They each only take in one input, and give back either one or no outputs (more on this later)
- On the bottom level are the "HELP_" and "REF_" files. Files that start with "HELP_" contain helper functions that assist the sizing functions defined in Component_Sizing. Files that start with "REF_" contain commonly used objects and functions that are referenced everywhere in the code.

### Function Flow
Within Turbofan_Main, we do three main things:
1) Update the TF object
2) Set up our input data structures
3) Call functions from Station_Thermo, Component_Sizing, Print_Results, and Plotting

**The TF Object**
The TF object is a data structure that contains all the relevant data for the entire engine generated during the cycle analysis and component sizing. Each time we run functions such as the cycle analysis or a component sizing script, the TF object gets updated with new values. The TF object itself is composed of many other objects as attributes, which themselves may have more object attributes. These can be referenced using periods. For example, the inlet mean radius of the low pressure compressor is referenced with "TF.compressor.LP.OUT.r_mean_1"

**Input Data Structures and Function IO**
The input data structures are dataclasses that hold in all the information that we send to our sizing functions. These input structures all have names that end with .IN, such as TF.compressor.LP.IN and TF.turbine.HP.IN. Every time we call a sizing or cycle function, the only input we give it is the corresponding .IN data structure. This keep Turbofan_Main tidy, and has the added benefit of making all of our inputs and design decisions easily readable. Likewise, each sizing or cycle function only returns one object, which then gets added to the TF object as a .OUT.

**Sizing Results**
Finally, Print_Results and Plotting each take in the entire TF object and outputs numerical values and graphs, respectively, to help the user understand what the engine is doing.