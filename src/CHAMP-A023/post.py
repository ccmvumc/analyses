import glob
import os

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import nibabel as nib
from nilearn.plotting import plot_roi, plot_stat_map, plot_anat
from nilearn.image import math_img, binarize_img, mean_img
from nilearn.masking import apply_mask


SUBJECTS_DIR = '/OUTPUTS/SUBJECTS'


def _subject_page(pdf, subject_dir):
    subject = os.path.basename(subject_dir)
    pet = f'{subject_dir}/esupravwm.output/rbv.nii.gz'
    mri = f'{subject_dir}/mri/orig.mgz'
    label = f'{subject_dir}/esupravwm.nii.gz'

    print(subject)

    if not os.path.isfile(pet):
        print(f'missing file:{pet}')
        return

    if not os.path.isfile(mri):
        print(f'missing file:{mri}')
        return

    if not os.path.isfile(label):
        print(f'missing file:{label}')
        return 

    # Make a letter paper size figure with 6 plots in 1 column
    fig, ax = plt.subplots(6, 1, figsize=(8.5,11))

    # Show ID in title
    fig.suptitle(subject)

    # Reduce whitespace
    plt.subplots_adjust(
        left=0.07,
        bottom=0.07,
        right=0.93,
        top=0.93,
        wspace=0.015,
        hspace=0.015,
    )

    # Make plots
    plot_stat_map(
        label,
        bg_img=pet,
        draw_cross=False,
        axes=ax[0],
        vmin=0,
        vmax=0.5,
        cmap='turbo',
        alpha=1.0,
    )

    disp = plot_anat(
        mri,
        draw_cross=False,
        axes=ax[1],
        colorbar=False,
        alpha=1.0,
    )

    # Show last 5 axial slices zoomed
    disp = plot_anat(
        pet,
        draw_cross=False,
        axes=ax[2],
        annotate=True,
        alpha=1.0,
    )

    disp = plot_stat_map(
        pet,
        bg_img=mri,
        draw_cross=False,
        display_mode='z',
        axes=ax[3],
        colorbar=False,
        annotate=True,
        vmin=0,
        vmax=0.5,
        cmap='turbo',
        alpha=1.0,
    )

    disp = plot_stat_map(
        pet,
        bg_img=mri,
        draw_cross=False,
        display_mode='z',
        axes=ax[4],
        colorbar=False,
        annotate=True,
        vmin=0,
        vmax=0.5,
        cmap='turbo',
        alpha=1.0,
    )

    pdf.savefig(fig, dpi=300)
    plt.close(fig)


# Find data
subjects = os.listdir(SUBJECTS_DIR)
print(f'{subjects=}')

# Make the PDF
print('make pdf')
with PdfPages('/OUTPUTS/report.pdf') as pdf:

    # Page for each subject
    for s in subjects:
        _subject_page(pdf, f'{SUBJECTS_DIR}/{s}')


print('PDF complete!')
