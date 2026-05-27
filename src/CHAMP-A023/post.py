import glob
import os

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from nilearn.plotting import plot_roi, plot_stat_map, plot_anat


AXIAL_SLICES = (-50, -25, 0, 25, 50)
CUT_COORDS = (0, 0, 0)


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


    #display = plot_roi(roi_img, bg_img)
    #coords = display.cut_coords


    # Plot MRI only
    plot_anat(
        mri_file,
        draw_cross=False,
        axes=ax[0],
        annotate=True,
        #cut_coords=CUT_COORDS,
        'MRI only',
    )

    # Plot PET only
    plot_anat(
        pet_file,
        draw_cross=False,
        axes=ax[1],
        annotate=True,
        #cut_coords=CUT_COORDS,
        vmax='auto',
        title='Realigned PET'
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
        title='esupravwm/MRI',
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
        title='GTM labels/MRI',
    )

    # Plot pet data on MRI
    plot_stat_map(
        rbv_file,
        bg_img=mri_file,
        draw_cross=False,
        display_mode='z',
        axes=ax[4],
        colorbar=False,
        annotate=True,
        cut_coords=AXIAL_SLICES,
        cmap='jet',
        vmax='auto',
        title='RBV/MRI',
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
        vmax='auto',
        cmap='gist_rainbow',
        title='GTM labels/PET',
    )

    pdf.savefig(fig, dpi=300)
    plt.close(fig)


def make_pdf(subject_dir, pdf_file):

    # Find data
    subjects = os.listdir(subject_dir)
    print(f'{subjects=}')

    # Make the PDF
    print('make pdf')
    pdf_file
    with PdfPages(pdf_file) as pdf:

        # Page for each subject
        for s in sorted(subjects):
            _subject_page(pdf, f'{subject_dir}/{s}')


    print('PDF complete!')


if __name__ == '__main__':
    subject_dir = sys.argv[1]
    pdf_file = sys.argv[2]

    print(f'Making pdf:{pdf_file}:subjects={subject_dir}')
    make_pdf(subject_dir, pdf_file)
    print('DONE!')
