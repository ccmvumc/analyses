clear batch;

% Manual for the conn_display tool 
% https://sites.google.com/view/conn/resources/conn-manual/conn_display

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

    % Load result, contrast 1, presets=2 for permutation
    disp('open display');
    h = conn_display(mat_file, 1, 2);

    % Print views
    disp('volume_print');
    conn_display(h, 'volume_print', fullfile(filelist(i).folder, 'preset2_volume.png'));

    disp('slice_print');
    conn_display(h, 'slice_print', fullfile(filelist(i).folder, 'preset2_slice.png'));

    % Then preset 1
    display('preset 1');
    conn_display(hf, 'fwec.option', 1);
    conn_display(h, 'volume_print', fullfile(filelist(i).folder, 'preset1_volume.png'));
    conn_display(h, 'slice_print', fullfile(filelist(i).folder, 'preset1_slice.png'));

    % Then preset 3
    display('preset 3');
    conn_display(hf, 'fwec.option', 3);
    conn_display(h, 'volume_print', fullfile(filelist(i).folder, 'preset3_volume.png'));
    conn_display(h, 'slice_print', fullfile(filelist(i).folder, 'preset3_slice.png'));

    % Then p<0.005
    display('preset 2, p<0.005');
    conn_display(hf, 'fwec.option', 2);
    conn_display(h, 'fwec.clusterlevel.value', 0.005);
    conn_display(h, 'volume_print', fullfile(filelist(i).folder, 'preset2_p0.005_volume.png'));
    conn_display(h, 'slice_print', fullfile(filelist(i).folder, 'preset2_p0.005_slice.png'));

    % Then p<0.05
    display('preset 2, p<0.05');
    conn_display(hf, 'fwec.option', 2);
    conn_display(h, 'fwec.clusterlevel.value', 0.05);
    conn_display(h, 'volume_print', fullfile(filelist(i).folder, 'preset2_p0.05_volume.png'));
    conn_display(h, 'slice_print', fullfile(filelist(i).folder, 'preset2_p0.05_slice.png'));
    
    % Finish up
    conn_display(h, 'close');
end
