import os, sys, shutil
from glob import glob

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from nilearn.glm.second_level import SecondLevelModel
from nilearn.plotting import plot_stat_map
from nilearn.plotting import plot_design_matrix
from nilearn.reporting import make_glm_report

from .params import CONTRASTS, CUT_COORDS, THRESHOLD, COLORMAP, VMAX

TITLE = 'COG-D N-Back Task'


def run_second_level(subjects_dir, group_dir, roi_dir):
    print(subjects_dir)
    print(group_dir)

    # Single t for each contrast
    for i, c in enumerate(CONTRASTS):
        cid = f'{i+1:04d}'
        print(f'Getting single t for contrast:{cid}')

        zmaps = glob(f'{subjects_dir}/*/*/contrast_{cid}_zmap.nii.gz')

        design_matrix = pd.DataFrame([1] * len(zmaps), columns=["intercept"])

        model = SecondLevelModel(smoothing_fwhm=8.0)

        model = model.fit(zmaps, design_matrix=design_matrix)

        zmap = model.compute_contrast(second_level_contrast="intercept", output_type="z_score")

        # Plot
        display = plot_stat_map(
            zmap,
            threshold=THRESHOLD,
            cut_coords=CUT_COORDS,
            display_mode='z',
            cmap=COLORMAP,
            title=f'{TITLE} 2nd-Level contrast_{cid}:{c}',
            vmax=VMAX
        )

        for r in glob(f'{roi_dir}/*.nii.gz'):
            display.add_contours(r, levels=[0.5], colors="r")


        # Save plot
        plt.savefig(f'{group_dir}/singlet_contrast_{cid}_report.pdf')

        plt.close()

        # Get the default report
        print('Second Level make_glm_report()')
        report = make_glm_report(model, contrasts=np.array([1]), cut_coords=CUT_COORDS)
        print(f'Saving report to: {group_dir}/contrast_{cid}_glm_report.html')
        report.save_as_html(f'{group_dir}/contrast_{cid}_glm_report.html')


def main(root_dir):
    subjects_dir = os.path.join(root_dir, 'SUBJECTS')
    group_dir = os.path.join(root_dir, 'GROUP')
    roi_dir = os.path.join(root_dir, 'ROIS')

    os.makedirs(group_dir, exist_ok=True)
    run_second_level(subjects_dir, group_dir, roi_dir)
