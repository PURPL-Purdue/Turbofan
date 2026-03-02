function starts = startsWith2(line, pattern)
%STARTSWITH2 Summary of this function goes here
%   Detailed explanation goes here
indices = strfind(line, pattern);
starts = ~isempty(indices) && indices(1) == 1;

end