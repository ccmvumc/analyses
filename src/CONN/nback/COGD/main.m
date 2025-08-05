%https://www.nitrc.org/forum/message.php?msg_id=14154

% Run single subject in CONN toolbox
CONTAINER = getenv("SINGULARITY_CONTAINER");
BIND = getenv("SINGULARITY_BIND");
ROOT = '/OUTPUTS';
FILTER=[0, Inf];
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
all_conditions = {};
all_onsets = {};
all_durations = {};
all_tr = 0.0;
all_times = [];

disp(pwd);
disp(BIND);
disp(CONTAINER);

if BIND == ""
    disp('no binds found for INPUTS/OUTPUTS');
    exit;
end

% Get list of subdirectories
subjects = dir(fullfile(ROOT, 'PREPROC'));

% Get just the directory names while excluding dot and double-dot
subjects = {subjects([subjects.isdir] & cellfun(@(d)~all(d == '.'), {subjects.name})).name};
disp(subjects);

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

        % Load slicetimes
        [nifti_dir, nifti_base, nifti_ext] = fileparts(fmris{n}{r});
        jsonfile = fullfile(nifti_dir, [nifti_base '.json']);
        jsondata = jsondecode(fileread(jsonfile));
        new_times = jsondata.SliceTiming;
        if isempty(all_times)
            all_times = new_times;
        elseif all_times ~= new_times
            disp('Conflicting slice times');
            exit;
        end

        % Load conditions from file
        load(fullfile(ROOT, 'PREPROC', subj, 'FMRI', sess, [scan '.conditions.mat']));

        disp(names);
        disp(onsets);
        disp(durations);
 
        if isempty(all_conditions)
            all_conditions = names;
        elseif ~isequal(all_conditions, names)
            disp('Conflicting conditions found');
            disp(all_conditions);
            disp(names);
            exit;
        end

        % Assign each condition to current subject indexed by n, current scan indexed by r, total run number
        for c=1:numel(names)
            condition = names{c};
            disp(condition);
            all_onsets{c}{n}{r} = onsets{c};
            all_durations{c}{n}{r} = durations{c};
        end

        % Increment total run count for subject
        r = r + 1;
    end
end

% Build the variable structure
var.ROOT = ROOT;
var.STRUCTURALS = anats;
var.FUNCTIONALS = fmris;
var.CONDITIONS = all_conditions;
var.ONSETS = all_onsets;
var.DURATIONS = all_durations;
var.TR = all_tr;
var.SLICETIMES = all_times;
disp(var);

NSUBJECTS=length(var.STRUCTURALS);

% Covariates, Second-Level subject effects, loaded after merging subjects
% Setup.subjects.effects, Setup.subjects.groups

clear batch;
batch.filename=fullfile(var.ROOT, 'conn_project.mat');

% Setup
batch.Setup.isnew=1;
batch.Setup.nsubjects=1;
batch.Setup.RT=var.TR;
batch.Setup.functionals=var.FUNCTIONALS;
batch.Setup.structurals=var.STRUCTURALS;
batch.Setup.rois.names = {};
batch.Setup.rois.dimensions = {};
batch.Setup.rois.files = {};

% Prepopulate secondary datasets so we can refer to subject-space in ROIs
batch.Setup.secondarydatasets{1}=struct('functionals_type', 2, 'functionals_label', 'unsmoothed volumes');
batch.Setup.secondarydatasets{2}=struct('functionals_type', 4, 'functionals_label', 'original data');
batch.Setup.secondarydatasets{3}=struct('functionals_type', 4, 'functionals_label', 'subject-space data');

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
batch.Setup.preprocessing.sliceorder=var.SLICETIMES;

% Configure to run and overwrite any existing
batch.Setup.done=1;
batch.Setup.overwrite=1;                            

% Configure denoising
batch.Denoising.filter=FILTER;
batch.Denoising.confounds.names={'White Matter', 'CSF', 'realignment', 'scrubbing'};
batch.Denoising.done=1;
batch.Denoising.overwrite=1;

% First-Level Analysis
batch.Analysis.analysis_number=1;
batch.Analysis.done=1;
batch.Analysis.overwrite=1;
batch.Analysis.sources = {
    'Effect of REST',
    'Effect of 0BACK',
    'Effect of 2BACK'
};

% Contrasts
batch.Results.analysis_number=1;
batch.Results.between_conditions.names={
    '0Back > Rest',
    '2Back > Rest',
    '2Back > 0Back'
};
batch.Results.between_conditions.contrasts={
    [-1 1 0],
    [-1 0 1],
    [0 -1 1]
};
batch.Results.done=1;
batch.Results.overwrite=1;

disp('Running batch with CONN');
conn_batch(batch);
disp('DONE!');
