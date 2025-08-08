'''CHAMP first level and second analysis of NBACK task, loads images processed by CONN toolbox'''

# INPUTS (per subject): 
#    in PREPROC subfolder FMRI/Baseline/
#      "dswuFMRI1.nii.gz" (these are the denosied/smoothed images)
#      "art_regression_outliers_and_movement_uFMRI1.mat" (only for displaying motion, not used in first-level b/c already denoised)
#      "FMRI1.nii.conditions.mat" (the spm format conditions we can load with scipy to make events table)
#    in subfolder FMRI/
#      "behavior.txt" (only for displaying)
#
# OUTPUTS:
#    PDF
#       -page per subject displaying data, contrast, motion params
#       -group pages for single t of contrast, with age, PLC vs MEC, with and without corrections
#
# TODO: read TR from files and verify, it's not in the denoised image header. do we need scan json?


import os, shutil
from glob import glob

import pandas as pd
import numpy as np
import scipy.io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from nilearn.glm.first_level import FirstLevelModel
from nilearn.glm.second_level import SecondLevelModel
from nilearn.plotting import plot_stat_map
from nilearn.plotting import plot_design_matrix
from nilearn.reporting import make_glm_report

from .params import TR, CONDITION_MAP, CONTRASTS, CUT_COORDS, DURATION, THRESHOLD, COLORMAP, VMAX


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

    events['trial_type'] = events['trial_type'].map(CONDITION_MAP)

    events['duration'] = DURATION

    print(events)

    # Specify model with parameters set for denoised CONN images
    print("Fitting a GLM")
    model = FirstLevelModel(
        t_r=TR,
        noise_model='ols',
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
            title=f'CHAMP N-Back 1st-Level contrast_{cid}:{c}',
            cmap=COLORMAP,
            vmax=VMAX
        )

        # Save plot
        plt.savefig(f'{output_dir}/contrast_{cid}_report.pdf')

        plt.close()

    # Get the default report
    report = make_glm_report(model, title='CHAMP N-Back Task', contrasts=np.array(CONTRASTS), cut_coords=CUT_COORDS)
    report.save_as_html(f'{output_dir}/glm_report.html')


def run_second_level(subjects_dir, group_dir):

    # Single t for each contrast
    for i, c in enumerate(CONTRASTS):
        cid = f'{i+1:04d}'
        print(f'Getting single t for contrast:{cid}')

        zmaps = glob(f'{subjects_dir}/*/contrast_{cid}_zmap.nii.gz')

        design_matrix = pd.DataFrame([1] * len(zmaps), columns=["intercept"])

        model = SecondLevelModel(smoothing_fwhm=8.0)

        model = model.fit(zmaps, design_matrix=design_matrix)

        zmap = model.compute_contrast(second_level_contrast="intercept", output_type="z_score")

        # Plot
        plot_stat_map(
            zmap,
            threshold=THRESHOLD,
            cut_coords=CUT_COORDS,
            display_mode='z',
            cmap=COLORMAP,
            title=f'CHAMP N-Back 2nd-Level contrast_{cid}:{c}',
            vmax=VMAX
        )

        # Save plot
        plt.savefig(f'{group_dir}/singlet_contrast_{cid}_report.pdf')

        plt.close()

        # Get the default report
        print('Second Level make_glm_report()')
        report = make_glm_report(model, contrasts=np.array([1]), cut_coords=CUT_COORDS)
        print(f'Saving report to: {group_dir}/contrast_{cid}_glm_report.html')
        report.save_as_html(f'{group_dir}/contrast_{cid}_glm_report.html')


def _write_subjects(subjects, filename):
    '''Writes a text file with one subject per line'''
    with open(filename, 'w') as f:
        f.write('\n'.join(subjects) + '\n')


def main():
    print('loading subjects')
    subjects = [x for x in os.listdir('/INPUTS') if os.path.isdir(f'/INPUTS/{x}')]
    include_subjects = []

    # Run each subject first level
    for subj in sorted(subjects):
        print(f'Preparing {subj}')

        try:
            subj_image = glob(f'/INPUTS/{subj}/assessors/*/*/*/*/d*.nii.gz')[0]
        except:
            try:    
                subj_image = glob(f'/INPUTS/{subj}/assessors/*/*/*/d*.nii.gz')[0]
            except:
                print(f'No d*.nii.gz for subject:{subj}')
                continue

        try:
            subj_mat = glob(f'/INPUTS/{subj}/assessors/*/*/*/*/*conditions.mat')[0]
        except:
            try:
                subj_mat = glob(f'/INPUTS/{subj}/assessors/*/*/*/*conditions.mat')[0]
            except:
                print(f'No conditions.mat for subject:{subj}')
                continue

        # Found everything so include this subject
        include_subjects.append(subj)

        subj_dir = f'/OUTPUTS/SUBJECTS/{subj}'

        if os.path.exists(subj_dir):
            print(f'skipping, exists:{subj_dir}')
            continue

        print(f'Running first-level:{subj}')
        os.makedirs(subj_dir, exist_ok=True)
        run_first_level(subj_image, subj_mat, subj_dir)

    # Save subject list
    _write_subjects(include_subjects, '/OUTPUTS/subjects.txt')

    # Now do group level
    subjects_dir = '/OUTPUTS/SUBJECTS'
    group_dir = '/OUTPUTS/GROUP'
    os.makedirs(group_dir, exist_ok=True)
    run_second_level(subjects_dir, group_dir)


if __name__ == '__main__':
    print('running main')
    main()
    print('ALL DONE!')
