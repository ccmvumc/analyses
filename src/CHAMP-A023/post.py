import glob
import os

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from nilearn.plotting import plot_roi, plot_stat_map, plot_anat


SUBJECTS_DIR = '/OUTPUTS/SUBJECTS'
AXIAL_SLICES = (-75, -50, -25, 0, 25, 50, 75)
CUT_COORDS = (0, 0, 0)


def _subject_page(pdf, subject_dir):
    subject = os.path.basename(subject_dir)
    pet_file = f'{subject_dir}/gtmpvc.esupravwm.output/rbv.nii.gz'
    mri_file = f'{subject_dir}/mri/orig.mgz'
    ref_file = f'{subject_dir}/esupravwm.nii.gz'
    gtm_file = f'{subject_dir}/mri/gtmseg.mgz'

    print(subject)

    if not os.path.isfile(pet_file):
        print(f'missing file:{pet_file}')
        return

    if not os.path.isfile(mri_file):
        print(f'missing file:{mri_file}')
        return

    if not os.path.isfile(ref_file):
        print(f'missing file:{ref_file}')
        return 


    if not os.path.isfile(gtm_file):
        print(f'missing file:{gtm_file}')
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

    # Plot PET only
    plot_anat(
        pet_file,
        #draw_cross=False,
        axes=ax[0],
        annotate=True,
        #cut_coords=CUT_COORDS,
    )

    # Plot MRI only
    plot_anat(
        mri_file,
        draw_cross=False,
        axes=ax[1],
        annotate=True,
        #cut_coords=CUT_COORDS,
    )

    # Plot reference region on mri
    plot_stat_map(
        ref_file,
        bg_img=mri_file,
        draw_cross=False,
        axes=ax[2],
        vmin=0,
        vmax=0.5,
        cmap='turbo',
        alpha=1.0,
        colorbar=False,
        #cut_coords=CUT_COORDS,
    )

    # Plot gtm labels on MRI
    plot_roi(
        gtm_file,
        bg_img=mri_file,
        draw_cross=False,
        axes=ax[3],
        colorbar=False,
        alpha=1.0,
        #cut_coords=CUT_COORDS,
    )

    # Plot pet data on MRI
    plot_stat_map(
        pet_file,
        bg_img=mri_file,
        draw_cross=False,
        display_mode='z',
        axes=ax[4],
        colorbar=False,
        annotate=True,
        cut_coords=AXIAL_SLICES,
        alpha=0.8,
        cmap='jet',
    )

    # Plot gtm labels on PET
    plot_roi(
        gtm_file,
        bg_img=pet_file,
        display_mode='z',
        axes=ax[5],
        colorbar=False,
        annotate=True,
        cut_coords=AXIAL_SLICES,
        alpha=0.5,
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
    for s in sorted(subjects):
        _subject_page(pdf, f'{SUBJECTS_DIR}/{s}')


print('PDF complete!')
