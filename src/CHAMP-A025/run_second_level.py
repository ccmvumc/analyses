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

from params import CONTRASTS, CUT_COORDS, THRESHOLD, COLORMAP, VMAX


TITLE = 'CHAMP N-Back Task'


def _run(subjects_dir, group_dir, roi_dir):
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
        #cid = f'{i+1:04d}'
        cid = str(i+1)
        print(f'Getting single t for contrast:{cid}')

        cmaps = glob(f'{subjects_dir}/*/conn_project/results/firstlevel/SBC_01/*_contrast{cid}.nii.gz')

        design_matrix = pd.DataFrame([1] * len(cmaps), columns=["intercept"])

        model = SecondLevelModel(smoothing_fwhm=8.0)

        model = model.fit(cmaps, design_matrix=design_matrix)

        zmap = model.compute_contrast(
            second_level_contrast="intercept",
            output_type="z_score"
        )

        zmap.to_filename(f'{group_dir}/contrast{cid}_zmap.nii.gz')

        # Plot
        display = plot_stat_map(
            zmap,
            threshold=THRESHOLD,
            cut_coords=CUT_COORDS,
            display_mode='z',
            cmap=COLORMAP,
            title=f'{TITLE} (n={len(cmaps)}) 2nd-Level single-t contrast_{cid}:{c}',
            vmax=VMAX
        )

        for r in glob(f'{roi_dir}/*.nii.gz'):
            display.add_contours(r, levels=[0.5], colors="g")

        # Save plot
        plt.savefig(f'{group_dir}/singlet_contrast{cid}_report.pdf')

        plt.close()

        # Get the default report
        print('Second Level make_glm_report()')
        report = make_glm_report(model, contrasts=np.array([1]), cut_coords=CUT_COORDS)
        print(f'Saving report to: {group_dir}/contrast{cid}_glm_report.html')
        report.save_as_html(f'{group_dir}/contrast{cid}_glm_report.html')


def _paired(subjects_dir, paired_dir, roi_dir):
    print(subjects_dir)
    print(paired_dir)

    # Single t for each contrast
    for i, c in enumerate(CONTRASTS):
        #cid = f'{i+1:04d}'
        cid = str(i+1)
        print(f'Getting paired-t for contrast:{cid}')

        mec_cmaps = sorted(glob(f'{subjects_dir}/*/conn_project/results/firstlevel/SBC_01/mec_contrast{cid}.nii.gz'))
        print(mec_cmaps)
        plc_cmaps = sorted(glob(f'{subjects_dir}/*/conn_project/results/firstlevel/SBC_01/plc_contrast{cid}.nii.gz'))
        print(plc_cmaps)

        n_subjects = len(mec_cmaps)

        subjects = [f'-{i+1:02d}' for i in range(n_subjects)] * 2
        conditions = ['MEC'] * n_subjects + ['PLC'] * n_subjects
        design_matrix = pd.DataFrame({
            'subject': subjects,
            'MEC-PLC': [1 if c == 'MEC' else -1 for c in conditions]
        })
        design_matrix = pd.get_dummies(design_matrix, columns=['subject'], drop_first=True).astype(float)

        plot_design_matrix(design_matrix)
        print(f'Save design matrix:{design_matrix}')
        plt.savefig(f'{paired_dir}/design.pdf', bbox_inches='tight')

        cmaps = mec_cmaps + plc_cmaps

        print(len(mec_cmaps), len(plc_cmaps), len(cmaps))

        model = SecondLevelModel(smoothing_fwhm=8.0)

        print('Fitting model')
        model = model.fit(cmaps, design_matrix=design_matrix)

        print('Computing contrast')
        zmap = model.compute_contrast('MEC-PLC')

        print(f'Saving:{zmap}')
        zmap.to_filename(f'{paired_dir}/contrast{cid}_zmap.nii.gz')

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
        plt.savefig(f'{paired_dir}/pairedt_contrast{cid}_report.pdf')

        plt.close()


def main(root_dir):
    subjects_dir = os.path.join(root_dir, 'SUBJECTS')
    group_dir = os.path.join(root_dir, 'GROUP')
    roi_dir = os.path.join(root_dir, 'ROIS')

    _run(subjects_dir, group_dir, roi_dir)


if __name__ == '__main__':
    import sys

    main(sys.argv[1])
