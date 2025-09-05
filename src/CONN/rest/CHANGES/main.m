% Run single rest subject with stc in CONN toolbox
SLICEORDER = 'interleaved (Philips)';
ROOT = '/OUTPUTS';
FILTER=[0.01, 0.1];
STEPS={
    'functional_label_as_original',...
    'functional_realign&unwarp',...
    'functional_slicetime',...
    'functional_art',...
    'functional_coregister_affine_noreslice',...
    'functional_label_as_subjectspace',...
    'functional_segment&normalize_direct',...
    'functional_label_as_mnispace',...
    'structural_center',...
    'structural_segment&normalize',...
    'functional_smooth',...
    'functional_label_as_smoothed'...
    };

anats = {};
fmris = {};
atlasfiles = {};
atlasnames = {};
atlasdatasets = {};
roifiles = {};
roidatasets = {};
conditions = {};
onsets = {};
durations = {};
all_tr = 0.0;
all_times = [];

disp(pwd);

% Get list of subdirectories
subjects = dir(fullfile(ROOT, 'PREPROC'));

% Get just the directory names while excluding dot and double-dot
subjects = {subjects([subjects.isdir] & cellfun(@(d)~all(d == '.'), {subjects.name})).name};
disp(subjects);

% Get list of rois
roinames = dir(fullfile(ROOT, 'ROI'));
roinames = {roinames([roinames.isdir] & cellfun(@(d)~all(d == '.'), {roinames.name})).name};
disp(roinames);

% Get list of atlas names to load for potential sources
if isfile(fullfile(ROOT, 'atlases.txt'))
    % Read first line
    atlasnames = readcell(fullfile(ROOT, 'atlases.txt'), Delimiter=' ');
else
    atlasnames = {};
end
disp(atlasnames);

% Get list of source regions (in addition to ROI list)
if isfile(fullfile(ROOT, 'sources.txt'))
    % Read first line into sources
    sources = readcell(fullfile(ROOT, 'sources.txt'), Delimiter=' ');
else
    sources = {};
end
disp(sources);

% Get current subject
n = 1;
subj = subjects{n};

% Assign the ANAT for the subject
anats{n} = fullfile(ROOT, 'PREPROC', subj, 'ANAT.nii');

% Get list of sessions
sessions = dir(fullfile(ROOT, 'PREPROC', subj, 'FMRI'));
sessions = {sessions([sessions.isdir] & cellfun(@(d)~all(d == '.'), {sessions.name})).name};

% Counter for total runs
r = 1;

% Assign each session
for k=1:numel(sessions)
    % Get current session
    sess = sessions{k};

    disp(sess);

    % Set name for the session-wide condition, all runs
    conditions{k} = ['rest-' sess];

    % Get list of scans for this session
    scans = dir(fullfile(ROOT, 'PREPROC', subj, 'FMRI', sess, '*.nii'));
    scans = {scans(~[scans.isdir]).name};

    % Assign each scan by appending to list for whole subject
    for s=1:numel(scans)
        scan = scans{s};
        disp(scan);

        % Set the scan file
        fmris{n}{r} = fullfile(ROOT, 'PREPROC', subj, 'FMRI', sess, scan);

        % Determine TR
        new_tr = spm_vol_nifti(fmris{n}{r}).private.timing.tspace;
        disp(new_tr);
        if all_tr == 0.0
            all_tr = new_tr;
        elseif all_tr ~= new_tr
            if abs(all_tr - new_tr) > 0.01
                disp('Conflicting TR found');
                disp(all_tr);
                disp(new_tr);
                exit;
            end
        end

        % Initialize all conditions for this run
        for c=1:numel(sessions)
            onsets{c}{n}{r} = [];
            durations{c}{n}{r} = [];
        end

        % Set onsets to 0 and duration to infinity to include whole scan.
        % Current scan indexed by total run number, r.
        % Set for condition for this session, k.
        onsets{k}{n}{r} = 0;
        durations{k}{n}{r} = inf;

        disp(onsets);
        disp(durations);

        % Increment total run count for subject
        r = r + 1;
    end
end

% Assign each roi
disp(roinames);
for i=1:numel(roinames)
    % Get current roi name
    roi = roinames{i};

    % Find the path to the roi file for this subject
    filename = dir(fullfile(ROOT, 'ROI', roi, subj));
    disp(filename);
    filename = {filename(~[filename.isdir]).name};
    filename = filename{1};
    roifiles{i}{n} = fullfile(ROOT, 'ROI', roi, subj, filename);
    roidatasets{i} = 'subject-space data';
end

% Assign each atlas file
disp(atlasnames);
for i=1:numel(atlasnames)
    atlas = atlasnames{i};
    atlasfiles{i}{n} = fullfile(ROOT, [atlas '.nii']);
    atlasdatasets{i} = 'unsmoothed volumes';
end
disp(atlasfiles);

% Build the variable structure
var.ROOT = ROOT;
var.STRUCTURALS = anats;
var.FUNCTIONALS = fmris;
var.CONDITIONS = conditions;
var.ONSETS = onsets;
var.DURATIONS = durations;
var.ROINAMES = [roinames atlasnames];
var.ROIFILES = [roifiles atlasfiles];
var.ROIDATASETS = [roidatasets atlasdatasets];
var.SOURCES = [roinames sources];
var.TR = all_tr;
disp(var);


clear batch;
batch.filename=fullfile(var.ROOT, 'conn_project.mat');

% Setup
batch.Setup.isnew=1;
batch.Setup.nsubjects=1;
batch.Setup.RT=var.TR;
batch.Setup.functionals=var.FUNCTIONALS;
batch.Setup.structurals=var.STRUCTURALS;
batch.Setup.analyses=[1];


% Prepopulate secondary datasets so we can refer to subject-space in ROIs
batch.Setup.secondarydatasets{1}=struct('functionals_type', 2, 'functionals_label', 'unsmoothed volumes');
batch.Setup.secondarydatasets{2}=struct('functionals_type', 4, 'functionals_label', 'original data');
batch.Setup.secondarydatasets{3}=struct('functionals_type', 4, 'functionals_label', 'subject-space data');

% Add ROIs
batch.Setup.rois.add = 1;
batch.Setup.rois.names=var.ROINAMES;
batch.Setup.rois.files=var.ROIFILES;
batch.Setup.rois.dataset=var.ROIDATASETS;

% Configure conditions
batch.Setup.conditions.names=var.CONDITIONS;
batch.Setup.conditions.onsets=var.ONSETS;
batch.Setup.conditions.durations=var.DURATIONS;

% Enable saving denoised NIFTIs with d prefix
% Optional output files:
%   outputfiles(1): 1/0 creates confound beta-maps
%   outputfiles(2): 1/0 creates confound-corrected timeseries
%   outputfiles(3): 1/0 creates seed-to-voxel r-maps
%   outputfiles(4): 1/0 creates seed-to-voxel p-maps
%   outputfiles(5): 1/0 creates seed-to-voxel FDR-p-maps
%   outputfiles(6): 1/0 creates ROI-extraction REX files
batch.Setup.outputfiles=[0,1,0,0,0,0];

% Configure preproc
batch.Setup.preprocessing.steps=STEPS;
batch.Setup.preprocessing.sliceorder=SLICEORDER;

% Configure to run and overwrite any existing
batch.Setup.done=1;
batch.Setup.overwrite=1;                            

% Configure denoising
batch.Denoising.filter=FILTER;
batch.Denoising.done=1;
batch.Denoising.overwrite=1;

% First-Level Analysis
batch.Analysis.analysis_number=1;
batch.Analysis.done=1;
batch.Analysis.overwrite=1;
batch.Analysis.sources=var.SOURCES;
batch.Analysis.weight='none';
batch.Analysis.type=1;

disp('Running batch with CONN');
conn_batch(batch);
disp('DONE!');
