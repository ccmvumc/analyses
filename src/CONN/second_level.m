clear batch;

% Load from .mat file into results
%load('/OUTPUTS/contrasts.mat')
%batch = contrasts;
load('/REPO/src/CONN/test/batch.mat')

%batch.filename = fileoutput;
%batch.Results.between_subjects.effect_names = ;
%batch.Results.between_subjects.contrast = ;
%batch.Results.between_conditions.effect_names = ;
%batch.Results.between_conditions.contrast =;
%batch.Results.between_sources.effect_names = ;
%batch.Results.between_sources.contrast = ;

batch.filename = '/OUTPUTS/conn.mat';

disp(batch);

conn_batch(batch);
