import os, shutil
from glob import glob

import pandas as pd
import numpy as np
import scipy.io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from nilearn.glm.first_level import FirstLevelModel
from nilearn.plotting import plot_stat_map
from nilearn.plotting import plot_design_matrix
from nilearn.reporting import make_glm_report

from .params import TR, CONTRASTS, CUT_COORDS, THRESHOLD, COLORMAP, VMAX


TITLE='COG-D N-Back Task'

def _load_events(conditions_file):
    mat = scipy.io.loadmat(conditions_file, simplify_cells=True)

    names = mat['names']
    onsets = mat['onsets']
    durations = mat['durations']

    return pd.DataFrame([
        {'onset': onset, 'duration': dur, 'trial_type': name}
        for name, onsets_, dur in zip(names, onsets, durations)
        for onset in onsets_
    ])


def run_first_level(image_file, conditions_file, output_dir):

    # Load conditions from file
    events = _load_events(conditions_file)

    events = events.sort_values('onset').reset_index(drop=True)

    print(events)

    # Specify model with parameters set for denoised CONN images
    # https://neurostars.org/t/nilearn-glm-first-level-question/29612
    print("Fitting a GLM")
    model = FirstLevelModel(
        t_r=TR,
        hrf_model='spm',
        drift_model=None,
        signal_scaling=False,
    )

    # Estimate fit
    model = model.fit(image_file, events=events)

    # Plot our design matrix
    _matrix = model.design_matrices_[0]
    plot_design_matrix(_matrix)
    plt.savefig(f'{output_dir}/design.pdf', bbox_inches='tight')

    # Contrast
    for i, c in enumerate(CONTRASTS):
        cid = f'{i+1:04d}'
        print(i, cid, c)

        zmap = model.compute_contrast(c, output_type='z_score')

        zmap.to_filename(f'{output_dir}/contrast_{cid}_zmap.nii.gz')

        # Plot
        plot_stat_map(
            zmap,
            threshold=THRESHOLD,
            display_mode='z',
            cut_coords=CUT_COORDS,
            title=f'{TITLE} 1st-Level contrast_{cid}:{c}',
            cmap=COLORMAP,
            vmax=VMAX
        )

        # Save plot
        plt.savefig(f'{output_dir}/contrast_{cid}_report.pdf')

        plt.close()

    # Get the default report
    report = make_glm_report(model, title=TITLE, contrasts=np.array(CONTRASTS), cut_coords=CUT_COORDS)
    report.save_as_html(f'{output_dir}/glm_report.html')


def _write_subjects(subjects, filename):
    '''Writes a text file with one subject per line'''
    with open(filename, 'w') as f:
        f.write('\n'.join(subjects) + '\n')


def main(input_dir, output_dir):
    #/Users/boydb1/Desktop/COGD-spin-fmri_nback_v2
    #9601/OUTPUTS/PREPROC/9601/FMRI/Baseline/dswauFMRI.nii.gz
    print('loading subjects')
    subjects = [x for x in os.listdir(input_dir) if os.path.isdir(f'{input_dir}/{x}')]
    include_subjects = []

    # Run each subject first level
    for subj in sorted(subjects):
        subj_dir = f'{output_dir}/SUBJECTS/{subj}'

        print(f'Preparing {subj}')

        try:
            baseline_image = glob(f'{input_dir}/{subj}/FMRI/Baseline/d*.nii.gz')[0]
            baseline_mat = glob(f'{input_dir}/{subj}/FMRI/Baseline/*conditions.mat')[0]
            week5_image = glob(f'{input_dir}/{subj}/FMRI/Week5/d*.nii.gz')[0]
            week5_mat = glob(f'{input_dir}/{subj}/FMRI/Week5/*conditions.mat')[0]
        except:
            try:
                baseline_image = glob(f'{input_dir}/{subj}/PREPROC/{subj}/FMRI/Baseline/d*.nii.gz')[0]
                subj_mat = glob(f'{input_dir}/{subj}/PREPROC/{subj}/FMRI/Baseline/*conditions.mat')[0]
                week5_image = glob(f'{input_dir}/{subj}/PREPROC/{subj}/FMRI/Week5/d*.nii.gz')[0]
                week5_mat = glob(f'{input_dir}/{subj}/PREPROC/{subj}/FMRI/Week5/*conditions.mat')[0]
            except Exception as err:
                print(f'failed to load subject:{subj}:{err}')
                continue

        # Found everything so include this subject
        include_subjects.append(subj)

        if os.path.exists(subj_dir):
            print(f'skipping, exists:{subj_dir}')
            continue

        print(f'Running first-level:{subj}:Baseline')
        _dir = f'{subj_dir}/Baseline'
        os.makedirs(_dir, exist_ok=True)
        run_first_level(baseline_image, baseline_mat, _dir)

        print(f'Running first-level:{subj}:Week5')
        _dir = f'{subj_dir}/Week5'
        os.makedirs(_dir, exist_ok=True)
        run_first_level(week5_image, week5_mat, _dir)

    # Save subject list
    _write_subjects(include_subjects, f'{output_dir}/subjects.txt')
