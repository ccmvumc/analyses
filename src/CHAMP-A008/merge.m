% Merges all conn.mat files into a single conn.mat

cd '/private/tmp/CHAMP-A008';
mkdir 'CONN';

% Merged mat file to save
fileoutput='CONN/conn.mat';

% Load all conn.mat
dirfiles = dir('OUTPUTS/**/conn_project.mat');

% Get a list of full paths
fileinputs = fullfile({dirfiles.folder}, {dirfiles.name});

% Load first file and save to initialize
conn('load', fileinputs{1});
conn('save', fileoutput);

% Merge all, note this will copy all the files, so check space
conn_merge(char(fileinputs), [], true, true);

% Run the postmerge step to verify
conn_process postmerge;

% Save the merged
conn('save', fileoutput);
