clear batch;

% Load contrasts from .mat file
load('/OUTPUTS/contrasts.mat');
disp(contrasts);

% Create batch for seed 2 voxel type
batch = contrasts;
batch.Analysis.type = 2;
batch.filename = '/OUTPUTS/conn.mat';
disp(batch);

% Run the second-level contrasts batch script with conn toolbox
conn_batch(batch);
