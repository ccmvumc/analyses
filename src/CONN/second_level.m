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

% Find second level mat files
filelist = dir(fullfile('/OUTPUTS/conn/results/secondlevel', '**', 'SPM.mat'));

% Load and save each
for i=1:length(filelist)
    matfile = fullfile(filelist(i).folder, 'SPM.mat');
    disp(mat_file);

    % Load result, contrast 1, presets 1
    % presets of 1 is CONN default for volume-based
    disp('open display');
    h = conn_display(mat_file, 1, 1);

    % Print views
    conn_display(h, 'volume_print', ['/OUTPUTS/volume_print-' num2str(i)  '.pdf']);        
    conn_display(h, 'slice_print', ['/OUTPUTS/slice_print-' num2str(i) '.pdf']);

    % close it
    disp('closing display');
    conn_display(h, 'close');
end
