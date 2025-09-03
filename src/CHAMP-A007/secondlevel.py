import os, shutil
from glob import glob

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from nilearn.glm.second_level import SecondLevelModel
from nilearn.plotting import plot_stat_map
from nilearn.plotting import plot_design_matrix
from nilearn.reporting import make_glm_report
from nilearn.datasets import fetch_atlas_schaefer_2018
from nilearn.image import load_img, math_img, new_img_like

from .params import CONTRASTS, CUT_COORDS, THRESHOLD, COLORMAP, VMAX, ROIS


TITLE = 'CHAMP N-Back Task'


def _make_masks(output_dir, rois):
    s100 = fetch_atlas_schaefer_2018(n_rois=100, yeo_networks=7, resolution_mm=2)
    s100_image = load_img(s100['maps'])
    s100_data = s100_image.get_fdata().astype(int)

    for r in rois:
        r_name = r['name']
        r_atlas = r['atlas']
        r_labels = np.array(r['labels'])

        if r_atlas == 'Schaefer100':
            r_mask = np.isin(s100_data, r_labels.astype(np.uint8))
            r_file = f'{output_dir}/{r_name}_mask.nii.gz'
            print(f'writing mask file:{r_file}')
            new_img_like(s100_image, r_mask).to_filename(r_file)
        else:
            print(f'atlas not supported:{r_atlas}')


def run_second_level(subjects_dir, group_dir, roi_dir):
    print(subjects_dir)
    print(group_dir)
    print(roi_dir)

    print('Second Level paired-t tests')
    paired_dir = f'{group_dir}/paired-t'
    os.makedirs(paired_dir, exist_ok=True)
    _paired(subjects_dir, paired_dir, roi_dir)

    single_dir = f'{group_dir}/single-t'
    os.makedirs(single_dir, exist_ok=True)
    _single(subjects_dir, single_dir, roi_dir)


def _single(subjects_dir, group_dir, roi_dir):
    print('Second Level single-t tests')

    # Single t for each contrast
    for i, c in enumerate(CONTRASTS):
        cid = f'{i+1:04d}'
        print(f'Getting single t for contrast:{cid}')

        zmaps = glob(f'{subjects_dir}/*/*/contrast_{cid}_zmap.nii.gz')

        design_matrix = pd.DataFrame([1] * len(zmaps), columns=["intercept"])

        model = SecondLevelModel(smoothing_fwhm=8.0)

        model = model.fit(zmaps, design_matrix=design_matrix)

        zmap = model.compute_contrast(second_level_contrast="intercept", output_type="z_score")

        zmap.to_filename(f'{group_dir}/contrast_{cid}_zmap.nii.gz')

        # Plot
        display = plot_stat_map(
            zmap,
            threshold=THRESHOLD,
            cut_coords=CUT_COORDS,
            display_mode='z',
            cmap=COLORMAP,
            title=f'{TITLE} (n={len(zmaps)}) 2nd-Level single-t contrast_{cid}:{c}',
            vmax=VMAX
        )

        for r in glob(f'{roi_dir}/*.nii.gz'):
            display.add_contours(r, levels=[0.5], colors="g")

        # Save plot
        plt.savefig(f'{group_dir}/singlet_contrast_{cid}_report.pdf')

        plt.close()

        # Get the default report
        print('Second Level make_glm_report()')
        report = make_glm_report(model, contrasts=np.array([1]), cut_coords=CUT_COORDS)
        print(f'Saving report to: {group_dir}/contrast_{cid}_glm_report.html')
        report.save_as_html(f'{group_dir}/contrast_{cid}_glm_report.html')


def _paired(subjects_dir, paired_dir, roi_dir):
    print(subjects_dir)
    print(paired_dir)

    # Single t for each contrast
    for i, c in enumerate(CONTRASTS):
        cid = f'{i+1:04d}'
        print(f'Getting paired-t for contrast:{cid}')

        mec_zmaps = sorted(glob(f'{subjects_dir}/*/MEC/contrast_{cid}_zmap.nii.gz'))
        plc_zmaps = sorted(glob(f'{subjects_dir}/*/PLC/contrast_{cid}_zmap.nii.gz'))

        n_subjects = len(mec_zmaps)

        subjects = [f'-{i+1:02d}' for i in range(n_subjects)] * 2
        conditions = ['MEC'] * n_subjects + ['PLC'] * n_subjects
        design_matrix = pd.DataFrame({
            'subject': subjects,
            'MEC-PLC': [1 if c == 'MEC' else -1 for c in conditions]
        })
        design_matrix = pd.get_dummies(design_matrix, columns=['subject'], drop_first=True).astype(float)

        plot_design_matrix(design_matrix)
        print('Save design matrix')
        plt.savefig(f'{paired_dir}/design.pdf', bbox_inches='tight')

        zmaps = mec_zmaps + plc_zmaps

        print(len(mec_zmaps), len(plc_zmaps), len(zmaps))

        model = SecondLevelModel(smoothing_fwhm=8.0)

        print('Fitting model')
        model = model.fit(zmaps, design_matrix=design_matrix)

        print('Computing contrast')
        zmap = model.compute_contrast('MEC-PLC')

        print(f'Saving:{zmap}')
        zmap.to_filename(f'{paired_dir}/contrast_{cid}_zmap.nii.gz')

        print(f'Plotting:{zmap}')
        display = plot_stat_map(
            zmap,
            threshold=THRESHOLD,
            cut_coords=CUT_COORDS,
            display_mode='z',
            cmap=COLORMAP,
            title=f'{TITLE} (n={n_subjects}) 2nd-Level paired-t contrast_{cid}:{c}',
            vmax=VMAX
        )

        for r in glob(f'{roi_dir}/*.nii.gz'):
            display.add_contours(r, levels=[0.5], colors="green")

        # Save plot
        plt.savefig(f'{paired_dir}/pairedt_contrast_{cid}_report.pdf')

        plt.close()


def main(root_dir):
    subjects_dir = os.path.join(root_dir, 'SUBJECTS')
    group_dir = os.path.join(root_dir, 'GROUP')
    roi_dir = os.path.join(root_dir, 'ROIS')

    run_second_level(subjects_dir, group_dir, roi_dir)
