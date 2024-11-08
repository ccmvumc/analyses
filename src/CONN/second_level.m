clear batch;

% Load contrasts from .mat file
load('/OUTPUTS/contrasts.mat');
disp(contrasts);

% Create batch
batch = contrasts;
batch.Analysis.measure = 1;
batch.filename = '/OUTPUTS/conn.mat';
disp(batch);

% Run the second-level contrasts batch script with conn toolbox
conn_batch(batch);
