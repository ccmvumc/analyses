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


def _subject_page(subject_dir):
    subject = os.path.basename(subject_dir)
    pet = f'{subject_dir}/esupravwm.output/rbv.nii.gz'
    mri = f'{subject_dir}/mri/orig.mgz'
    label = f'{subject_dir}/esupravwm.nii.gz'

    print(subject)

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

    # load data from subject image masked by
    #df = pd.DataFrame({'LCR': apply_mask(cr, lh_mask)})
    #df = pd.concat([df, pd.DataFrame({'RCR': apply_mask(cr, rh_mask)})])
    #df = pd.concat([df, pd.DataFrame({'TCR': apply_mask(cr, tot_mask)})])
    #df = df.rename(columns={
    #    'LCR': f'Left CR\nmean={df.LCR.mean():.2f}',
    #    'RCR': f'Right CR\nmean={df.RCR.mean():.2f}',
    #    'TCR': f'Total CR\nmean={df.TCR.mean():.2f}',
    #})

    # Create the boxplot of CR values
    #df.boxplot(ax=ax[5], showfliers=True, patch_artist=True)
    #ax[5].set_ylim(-0.01, 0.5)

    # Color each box
    #colors = ['lawngreen', 'red', 'brown']
    #for patch, color in zip(ax[5].patches, colors):
    #    patch.set_facecolor(color)

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
