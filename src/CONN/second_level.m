clear batch;
fileoutput='/OUTPUTS/conn.mat';

% Load from .mat file into results
load('/OUTPUTS/contrasts.mat')

%batch.filename = fileoutput;
%batch.Results.between_subjects.effect_names = ;
%batch.Results.between_subjects.contrast = ;
%batch.Results.between_conditions.effect_names = ;
%batch.Results.between_conditions.contrast =;
%batch.Results.between_sources.effect_names = ;
%batch.Results.between_sources.contrast = ;

batch = contrasts;
disp(batch);

conn_batch(batch);
