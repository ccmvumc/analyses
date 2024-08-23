% Merges all conn.mat files into a single conn.mat

% Merged mat file to save
fileoutput='/OUTPUTS/conn.mat';

% Load all conn.mat in /INPUTS
dirfiles = dir('/INPUTS/**/conn.mat')

% Get a list of full paths
fileinputs = fullfile({dirfiles.folder}, {dirfiles.name});

% Load first file and save to initialize
conn('load', fileinputs{1});
conn('save', fileoutput);

% Merge all
conn_merge(char(fileinputs), [], true, true);

% Run the postmerge step to verify
conn_process postmerge;

% Save the merged
conn('save', fileoutput);
