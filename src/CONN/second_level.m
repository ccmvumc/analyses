clear batch;

% Load contrasts from .mat file
load('/OUTPUTS/contrasts.mat');
disp(batch);

% Run the second-level contrasts batch script with conn toolbox
conn_batch(batch);

% Find second level mat files
filelist = dir(fullfile('/OUTPUTS/conn/results/secondlevel', '**', 'SPM.mat'));

% Load and save each
for i=1:length(filelist)
    mat_file = fullfile(filelist(i).folder, 'SPM.mat');

    disp(mat_file);

    % Load result, contrast 1, presets 1 (CONN default for volume-based)
    disp('open display');
    h = conn_display(mat_file, 1, 1);

    % Print views
    disp('volume_print');
    conn_display(h, 'volume_print', fullfile(filelist(i).folder, 'volume_print.png'));

    disp('slice_print');
    conn_display(h, 'slice_print', fullfile(filelist(i).folder, 'slice_print.png'));

    disp('glass_print');
    conn_display(h, 'glass_print', fullfile(filelist(i).folder, 'glass_print.png'));

    % close it
    disp('closing display');
    conn_display(h, 'close');
end
