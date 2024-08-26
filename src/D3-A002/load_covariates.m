% Setup.subjects.effect_names  : subjects.effect_names{neffect} char array of second-level covariate name
% Setup.subjects.effects       : subjects.effects{neffect} vector of size [nsubjects,1] defining second-level effects
% Setup.subjects.descrip       : (optional) subjects.descrip{neffect} char array of effect description (long name; for display purposes only)
% Setup.subjects.add           : use 1 to define an additional set of covariates

% Setup.subjects.group_names   : subjects.group_names{ngroup} char array of second-level group name
% Setup.subjects.groups        : subjects.group vector of size [nsubjects,1] (with values from 1 to ngroup) defining subject groups
% Setup.subjects.descrip       : (optional) subjects.descrip{neffect} char array of group description (long name; for display purposes only)
% Setup.subjects.add           : use 1 to define an additional set of covariates

clear batch;

% Load from .mat file
load('/OUTPUTS/covariates.mat')

batch.filename=fullfile(cwd, '/OUTPUTS/conn.mat');
batch.Setup.subjects.effect_names=effect_names;
batch.Setup.subjects.effects=effects;
batch.Setup.subjects.add=1;

disp(batch);

conn_batch(batch);
