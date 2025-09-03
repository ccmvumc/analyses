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
from nilearn.datasets import fetch_atlas_schaefer_2018
from nilearn.image import load_img, math_img, new_img_like
from nilearn.masking import apply_mask

from .params import TR, CONTRASTS, CUT_COORDS, THRESHOLD, COLORMAP, VMAX, ROIS


TITLE='CHAMP N-Back Task'


def _make_roi_masks(output_dir, rois):
    s200 = fetch_atlas_schaefer_2018(n_rois=200, yeo_networks=7, resolution_mm=2)
    s200_image = load_img(s200['maps'])
    s200_data = s200_image.get_fdata().astype(int)

    for r in rois:
        r_name = r['name']
        r_atlas = r['atlas']
        r_labels = np.array(r['labels'])

        if r_atlas == 'Schaefer200':
            r_mask = np.isin(s200_data, r_labels.astype(np.uint8))
            r_file = f'{output_dir}/{r_name}_mask.nii.gz'
            print(f'writing mask file:{r_file}')
            new_img_like(s200_image, r_mask).to_filename(r_file)
        else:
            print(f'atlas not supported:{r_atlas}')


def _load_events(conditions_file):
    mat = scipy.io.loadmat(conditions_file, simplify_cells=True)

    names = mat['names']
    onsets = mat['onsets']
    durations = mat['durations']

    df = pd.DataFrame([
        {'onset': onset, 'duration': dur, 'trial_type': name}
        for name, onsets_, dur in zip(names, onsets, durations)
        for onset in onsets_
    ])

    df = df.sort_values('onset').reset_index(drop=True)

    df = _merge_blocks(df)

    return df


def _merge_blocks(df):
    # Get a block number for each row
    df['block'] = (df['trial_type'] != df['trial_type'].shift()).cumsum()

    # Merge by block number, onset at first row of block and sum durations
    df = (df.groupby(['block', 'trial_type'], as_index=False).agg({'onset': 'first', 'duration': 'sum'}))

    # Drop intermediate columns
    df = df.drop(columns='block').reset_index(drop=True)

    return df


def _roi_mean(image, mask):
    masked_data = apply_mask(image, mask)
    return np.mean(masked_data)


def _fit_model(image_file, events):
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

    return model


def _contrasts(model, contrasts, output_dir, roi_dir):
    # Compute each contrast and plot
    for i, c in enumerate(contrasts):
        cid = f'{i+1:04d}'
        print(i, cid, c)

        zmap = model.compute_contrast(c, output_type='z_score')

        zmap.to_filename(f'{output_dir}/contrast_{cid}_zmap.nii.gz')

        # Plot
        display = plot_stat_map(
            zmap,
            threshold=THRESHOLD,
            display_mode='z',
            cut_coords=CUT_COORDS,
            title=f'{TITLE} 1st-Level contrast_{cid}:{c}',
            cmap=COLORMAP,
            vmax=VMAX
        )

        for r in glob(f'{roi_dir}/*.nii.gz'):
            display.add_contours(r, levels=[0.5], colors="g")

        # Save plot
        plt.savefig(f'{output_dir}/contrast_{cid}_report.pdf')

        plt.close()


def _extract_rois(output_dir, roi_dir):
    data = {}
    masks = glob(f'{roi_dir}/*.nii.gz')
    zmap = f'{output_dir}/contrast_0001_zmap.nii.gz'

    for m in masks:
        r = os.path.basename(m).split('_mask.nii.gz')[0]
        data[f'{r}'] = _roi_mean(zmap, m)

    return data


def run_first_level(image_file, conditions_file, output_dir, roi_dir):
    # Load conditions from file
    events = _load_events(conditions_file)
    print(events)

    # Fit event data to image data
    print('Fitting  model')
    model = _fit_model(image_file, events)

    # Plot our design matrix
    design_matrix = model.design_matrices_[0]
    plot_design_matrix(design_matrix)
    print('Save design matrix')
    plt.savefig(f'{output_dir}/design.pdf', bbox_inches='tight')

    # Plot the contrasts
    print('contrasts')
    _contrasts(model, CONTRASTS, output_dir, roi_dir)

    # Get the default report
    print('make default report')
    report = make_glm_report(model, title='CHAMP N-Back Task', contrasts=np.array(CONTRASTS), cut_coords=CUT_COORDS)
    report.save_as_html(f'{output_dir}/glm_report.html')

    # Extract ROI means from 2BACK-0BACK contrast
    stats = _extract_rois(output_dir, roi_dir)
    filename = f'{output_dir}/stats.txt'
    print(f'extracting:{filename}')
    _write_stats(stats, filename)


def _write_stats(stats, filename):
    '''Writes a text file with key/value per line'''
    with open(filename, 'w') as f:
        for k in sorted(stats):
            f.write(f'{k}={stats[k]:.3f}\n')


def _write_subjects(subjects, filename):
    '''Writes a text file with one subject per line'''
    with open(filename, 'w') as f:
        f.write('\n'.join(subjects) + '\n')


def _run_subject(plc_image, plc_mat, mec_image, mec_mat, output_dir, roi_dir):
    plc_dir = f'{output_dir}/PLC'
    mec_dir = f'{output_dir}/MEC'

    print(f'Running first-level:PLC:{plc_dir}')
    os.makedirs(plc_dir, exist_ok=True)
    run_first_level(plc_image, plc_mat, plc_dir, roi_dir)

    print(f'Running first-level:MEC:{mec_dir}')
    os.makedirs(mec_dir, exist_ok=True)
    run_first_level(mec_image, mec_mat, mec_dir, roi_dir)


def main(input_dir, output_dir):
    print('making masks')
    roi_dir = f'{output_dir}/ROIS'
    os.makedirs(roi_dir, exist_ok=True)
    _make_roi_masks(roi_dir, ROIS)

    print('loading subjects')
    subjects = sorted([x for x in os.listdir(input_dir) if os.path.isdir(f'{input_dir}/{x}')])
    print(subjects)
    include_subjects = []

    # Run each subject first level
    for subj in subjects:
        subj_dir = f'{output_dir}/SUBJECTS/{subj}'

        print(f'Checking {subj}')
        try:
            plc_img = glob(f'{input_dir}/{subj}/**/PLC/d*.nii.gz', recursive=True)[0]
            plc_mat = glob(f'{input_dir}/{subj}/**/PLC/*conditions.mat', recursive=True)[0]
            mec_img = glob(f'{input_dir}/{subj}/**/MEC/d*.nii.gz', recursive=True)[0]
            mec_mat = glob(f'{input_dir}/{subj}/**/MEC/*conditions.mat', recursive=True)[0]
        except Exception as err:
            print(f'failed to load subject:{subj}:{err}')
            continue

        # Found everything so include this subject
        include_subjects.append(subj)

        if os.path.exists(subj_dir):
            print(f'skipping, exists:{subj_dir}')
            continue

        print(f'Running first-level:{subj}')
        _run_subject(plc_img, plc_mat, mec_img, mec_mat, subj_dir, roi_dir)

    # Save subject list
    _write_subjects(include_subjects, '/OUTPUTS/subjects.txt')
