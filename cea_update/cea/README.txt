MATLAB CEA wrapper for rocket problems that allows for multiple fuel/oxidizer
entry and unlimited pressure, mixture, and ratio inputs (usually limited by CEA
to around 14 each). Data is output in a convenient MATLAB containers.Map data
type that stores all performance, compressible flow, thermal property, and
molar concentration values normally seen in a standard CEA '.out' file. See
'cea_rocket_example.m' for an example script and type 'help {file}' where
{file} could be any of the MATLAB functions provided.

Installation
Store the parent folder 'cea/' on your local computer. This will speed up
computations as Windows won't have to reach through a network drive for the
data files. Note that this means you should run the functions locally as well
to see the full performance benefits. Then add the 'cea/' folder to your MATLAB
local path. This can be done with the following MATLAB commands.

addpath('C:\path\to\cea\', '-end');
savepath();