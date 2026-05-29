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
    mat_dir = filelist(i).folder
    mat_file = fullfile(mat_dir, 'SPM.mat');

    disp(mat_file);

    % Load result, contrast 1, presets=2 for permutation
    disp('open display');

    h = conn_display(mat_file, 1, 1);

    display('preset 1');

    % Print views
    disp('volume_print');
    conn_display(h, 'volume_print', fullfile(mat_dir, 'preset1_volume.png'));

    disp('slice_print');
    conn_display(h, 'slice_print', fullfile(mat_dir, 'preset1_slice.png'));

    display('preset 1, p<0.005');
    conn_display(h, 'fwec.clusterlevel.value', 0.005);
    conn_display(h, 'volume_print', fullfile(mat_dir, 'preset1_p0.005_volume.png'));
    conn_display(h, 'slice_print', fullfile(mat_dir, 'preset1_p0.005_slice.png'));

    display('preset 1, p<0.05');
    conn_display(h, 'fwec.clusterlevel.value', 0.05);
    conn_display(h, 'volume_print', fullfile(mat_dir, 'preset1_p0.05_volume.png'));
    conn_display(h, 'slice_print', fullfile(mat_dir, 'preset1_p0.05_slice.png'));

    conn_display(h, 'close');

    % Then preset 2
    display('preset 2');
    h = conn_display(mat_file, 1, 2);
    conn_display(h, 'volume_print', fullfile(mat_dir, 'preset2_volume.png'));
    conn_display(h, 'slice_print', fullfile(mat_dir, 'preset2_slice.png'));

    % Then p<0.005
    display('preset 2, p<0.005');
    conn_display(h, 'fwec.clusterlevel.value', 0.005);
    conn_display(h, 'volume_print', fullfile(mat_dir, 'preset2_p0.005_volume.png'));
    conn_display(h, 'slice_print', fullfile(mat_dir, 'preset2_p0.005_slice.png'));

    % Then p<0.05
    display('preset 2, p<0.05');
    conn_display(h, 'fwec.clusterlevel.value', 0.05);
    conn_display(h, 'volume_print', fullfile(mat_dir, 'preset2_p0.05_volume.png'));
    conn_display(h, 'slice_print', fullfile(mat_dir, 'preset2_p0.05_slice.png'));

    % Finally preset 3
    display('preset 3');
    h = conn_display(mat_file, 1, 3);
    conn_display(h, 'volume_print', fullfile(mat_dir, 'preset3_volume.png'));
    conn_display(h, 'slice_print', fullfile(mat_dir, 'preset3_slice.png'));

    % Then p<0.005
    display('preset 3, p<0.005');
    conn_display(h, 'fwec.clusterlevel.value', 0.005);
    conn_display(h, 'volume_print', fullfile(mat_dir, 'preset3_p0.005_volume.png'));
    conn_display(h, 'slice_print', fullfile(mat_dir, 'preset3_p0.005_slice.png'));

    % Then p<0.05
    display('preset 3, p<0.05');
    conn_display(h, 'fwec.clusterlevel.value', 0.05);
    conn_display(h, 'volume_print', fullfile(mat_dir, 'preset3_p0.05_volume.png'));
    conn_display(h, 'slice_print', fullfile(mat_dir, 'preset3_p0.05_slice.png'));

    % Finish up
    conn_display(h, 'close');
end
