import glob
import os
import sys

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from nilearn.plotting import plot_roi, plot_stat_map, plot_anat


def _subject_page(pdf, subject_dir):
    subject = os.path.basename(subject_dir)
    pet_file = f'{subject_dir}/rPET.nii.gz'
    mri_file = f'{subject_dir}/mri/orig.mgz'
    ref_file = f'{subject_dir}/esupravwm.nii.gz'
    gtm_file = f'{subject_dir}/mri/gtmseg.mgz'
    rbv_file = f'{subject_dir}/gtmpvc.esupravwm.output/rbv.nii.gz'

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

    print(plt.rcParams.get('font.size', 'Not Found'))

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

    # Plot gtm labels on MRI
    disp = plot_roi(
        gtm_file,
        bg_img=mri_file,
        draw_cross=False,
        axes=ax[3],
        colorbar=False,
        alpha=1.0,
    )
    disp.title('GTM labels/MR', size=6)

    gtm_coords = disp.cut_coords

    mid_axial = gtm_coords[2]

    axial_slices = [
        mid_axial - 50,
        mid_axial - 25,
        mid_axial,
        mid_axial + 25,
        mid_axial + 50,
    ]

    # Plot MRI only
    disp = plot_anat(
        mri_file,
        draw_cross=False,
        axes=ax[0],
        annotate=True,
        cut_coords=gtm_coords,
        threshold='auto',
    )
    disp.title('MRI only', size=6)

    # Plot PET only
    disp = plot_anat(
        pet_file,
        draw_cross=False,
        axes=ax[1],
        annotate=True,
        cut_coords=gtm_coords,
        threshold='auto',
    )
    disp.title('Realigned PET', size=6)

    # Plot reference region on mri
    disp = plot_stat_map(
        ref_file,
        bg_img=mri_file,
        draw_cross=False,
        axes=ax[2],
        vmin=0,
        vmax=0.5,
        cmap='turbo',
        alpha=1.0,
        colorbar=False,
        cut_coords=gtm_coords,
    )
    disp.title('esupravwm/MRI', size=6)

    # Plot pet data on MRI
    disp = plot_stat_map(
        rbv_file,
        bg_img=mri_file,
        draw_cross=False,
        display_mode='z',
        axes=ax[4],
        colorbar=False,
        annotate=True,
        cut_coords=axial_slices,
        cmap='jet',
        threshold='auto',
    )
    disp.title('RBV/MRI', size=6)

    # Plot gtm labels on PET
    disp = plot_roi(
        gtm_file,
        bg_img=pet_file,
        display_mode='z',
        axes=ax[5],
        colorbar=False,
        annotate=True,
        cut_coords=axial_slices,
        threshold='auto',
        cmap='gist_rainbow',
    )
    disp.title('GTM labels/PET', size=6)

    # Put page number in footer
    fig.text(0.5, 0.05, f'Page {pdf.get_pagecount() + 1}', ha='center', fontsize=8, color='gray')

    pdf.savefig(fig, dpi=300)
    plt.close(fig)


def make_pdf(subject_dir, pdf_file):

    # Find data
    subjects = sorted(os.listdir(subject_dir))
    print(f'{subjects=}')

    # Make the PDF
    print('make pdf')
    with PdfPages(pdf_file) as pdf:
        # Page for each subject
        for s in subjects:
            _subject_page(pdf, f'{subject_dir}/{s}')

    print('PDF complete!')


if __name__ == '__main__':
    subject_dir = sys.argv[1]
    pdf_file = sys.argv[2]

    print(f'Making pdf:{pdf_file}:subjects={subject_dir}')
    make_pdf(subject_dir, pdf_file)
    print('DONE!')
