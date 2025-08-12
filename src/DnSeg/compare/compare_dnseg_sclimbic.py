import os
from glob import glob

import numpy as np
from scipy.ndimage import center_of_mass
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from nilearn.image.resampling import coord_transform
from nilearn.image import load_img, new_img_like, resample_img, math_img
from nilearn.masking import intersect_masks
from nilearn.plotting import plot_roi, plot_anat, find_parcellation_cut_coords
from matplotlib_venn import venn2
from pypdf import PdfWriter


# INPUTS: directory with subdirectory SUBJECTS with a subdir per subject
# OUTPUTS: report.pdf at top level, volumes.txt and report in each subject dir


def calculate_volumes(dnseg, sclimbic):
    ''' Return volume of each ROI and volume of intersection, per hemisphere'''

    volumes = {}

    # Load images
    sclimbic_img = load_img(sclimbic)
    dnseg_img = load_img(dnseg)
    dnseg_img = resample_img(
        dnseg_img,
        target_shape=sclimbic_img.shape,
        target_affine=sclimbic_img.affine,
        interpolation='nearest',
        copy_header=True,
        force_resample=True
    )

    dnseg_data = dnseg_img.get_fdata()
    sclimbic_data = sclimbic_img.get_fdata()

    voxel_dims = dnseg_img.header['pixdim'][1:4]
    print(f'{voxel_dims=}')

    vox_size = voxel_dims[0] * voxel_dims[1] * voxel_dims[2]
    print(f'{vox_size=}')

    volumes['dnseg_lh'] = np.sum(dnseg_data == 1) * vox_size
    volumes['dnseg_rh'] = np.sum(dnseg_data == 2) * vox_size

    volumes['sclimbic_lh'] = np.sum(sclimbic_data == 865) * vox_size
    volumes['sclimbic_rh'] = np.sum(sclimbic_data == 866) * vox_size

    _intersect = intersect_masks([
        new_img_like(dnseg_img, dnseg_data == 1.0), 
        new_img_like(dnseg_img, sclimbic_data == 865.0)
    ], threshold=1)
    volumes['intersect_lh'] = np.sum(_intersect.get_fdata() > 0) * vox_size

    _intersect = intersect_masks([
        new_img_like(dnseg_img, dnseg_data == 2.0), 
        new_img_like(dnseg_img, sclimbic_data == 866.0)
    ], threshold=1)
    volumes['intersect_rh'] = np.sum(_intersect.get_fdata() > 0) * vox_size

    return volumes


def _load_volumes(filename):
    '''Load volumes from key=value per line adn return dict'''
    volumes = {}

    # Load each line as key/value pair
    with open(filename, "r") as f:
        for line in f:
            k, v = line.split('=')
            volumes[k] = v

    return volumes


def _calculate_summary(root_dir):
    '''Calculate summary of subjects, means and counts, returns dict'''

    data = []
    summary = {}
    rois = ['dnseg', 'sclimbic', 'intersect']

    subj_dir = os.path.join(root_dir, 'SUBJECTS')

    print(f'Loading subjects from {subj_dir}')
    for d in sorted(os.listdir(subj_dir)):
        if d.startswith('.'):
            continue

        print(d)
        vols = _load_volumes(os.path.join(subj_dir, d, 'volumes.txt'))
        vols['SUBJECT'] = d
        data.append(vols)

    df = pd.DataFrame(d)
    print(df)

    for roi in []
        for hemi in ['lh', 'rh']:
            summary[f'mean_{roi}_{hemi}'] = df[f'{roi}_{hemi}'].mean()

    summary['count_sessions'] = len(df)        

    return summary


def _make_summary(root_dir):
    '''Make summary pdf'''
    pdf_file = os.path.join(root_dir, 'report.pdf')
    summary = _calculate_summary(root_dir)

    session_count = summary['count_sessions']

    # Make the PDF
    print('Making pdf')
    with PdfPages(pdf_file) as pdf:

        fig, ax = plt.subplots(5, 2, figsize=(8.5,11))

        fig.suptitle(f'DnSeg vs. sclimbic\nSummary n={session_count}')

        # Plot the venn row
        print('Plotting venn diagrams')
        volumes = {}
        for roi in ['dnseg', 'sclimbic', 'intersect']:
            for hemi in ['lh', 'rh']:
                volumes[f'{roi}_{hemi}'] = summary[f'mean_{roi}_{hemi}']

        _plot_venn(volumes, ax[0])

        # Tigthen up margins
        plt.subplots_adjust(
            left=0.07,
            bottom=0.07,
            right=0.93,
            top=0.93,
            wspace=0.05,
            hspace=0.15,
        )

        # Save to PDF
        print(f'saving pdf:{pdf_file}')
        pdf.savefig(fig, dpi=300)

    plt.close()


def _plot_venn(volumes, ax):
    '''Plot venn diagrams of dnseg vs sclimbic for Left/Right'''

    # Make left venn in first column
    venn2(
        subsets=(
            volumes['dnseg_lh'],
            volumes['sclimbic_lh'],
            volumes['intersect_lh'],
        ),
        set_labels=('DnSeg NBM', 'sclimbic BF', ''),
        set_colors=['red', 'lime'],
        alpha=0.7,
        ax=ax[0],
    )
    ax[0].set_title('Left Hemisphere\nVolume (mm^3)')

    # Make right venn in second column
    venn2(
        subsets=(
            volumes['dnseg_rh'],
            volumes['sclimbic_rh'],
            volumes['intersect_rh'],
        ),
        set_labels=('DnSeg NBM', 'sclimbic BF', ''),
        set_colors=['fuchsia', 'deepskyblue'],
        alpha=0.7,
        ax=ax[1]
    )
    ax[1].set_title('Right Hemisphere\nVolume (mm^3)')


def _zoom_ortho(disp, coords):
    '''Zoom all 3 displays of an orth view by adjusting axis limtis'''

    # zoom in mmillimeters
    ZMX = 20 
    ZMY = 30

    x = coords[0]
    y = coords[1]
    z = coords[2]

    # Coronal
    disp.axes['y'].ax.set_xlim(x - ZMX, x + ZMX)
    disp.axes['y'].ax.set_ylim(z - ZMY, z + ZMY)

    # Sagittal
    disp.axes['x'].ax.set_xlim(y - ZMX, y + ZMX)
    disp.axes['x'].ax.set_ylim(z - ZMY, z + ZMY)

    # Axial
    disp.axes['z'].ax.set_xlim(x - ZMX, x + ZMX)
    disp.axes['z'].ax.set_ylim(y - ZMY, y + ZMY)


def _save_volumes(volumes, filename):
    '''Write text file with behavior values'''
    with open(filename, "w") as f:
        for k in sorted(volumes):
            f.write("%s=%s\n" % (k, volumes[k]))


def _process_subject(subject_dir):
    '''Process a subject, outputs are volumes text file and a PDF report'''
    sclimbic_file = subject_dir + '/nu.sclimbic.mgz'
    dnseg_file = subject_dir + '/T1_seg.nii.gz'
    anat_file = subject_dir + '/T1_resliced.nii.gz'
    pdf_file = subject_dir + '/report.pdf'
    vol_file = subject_dir +'/volumes.txt'

    if os.path.exists(vol_file) and os.path.exists(pdf_file):
        print(f'exists:{vol_file}:{pdf_file}')
        return

    print('calculating volumes for comparison')
    volumes = calculate_volumes(dnseg_file, sclimbic_file)
    _save_volumes(volumes, subject_dir +'/volumes.txt')

    # Find coordinates of center of mass for each ROI separate hemispheres
    print('finding center-of-mass coordinates for plotting')

    # Load dnseg
    roi_img = load_img(dnseg_file)
    roi_data = roi_img.get_fdata()
    roi_affine = roi_img.affine

    # Left DnSeg
    _x,_y,_z = center_of_mass(roi_data, labels=roi_data, index=1)
    _coords = coord_transform(_x,_y,_z, roi_affine)
    coords_dnseg_lh = _coords

    # Right DnSeg
    _x,_y,_z = center_of_mass(roi_data, labels=roi_data, index=2)
    _coords = coord_transform(_x,_y,_z, roi_affine)
    coords_dnseg_rh = _coords

    _coords, _names = find_parcellation_cut_coords(sclimbic_file, return_label_names=True)
    # TODO: use names to confirm label id   
    coords_sclimbic_lh = _coords[9]
    coords_sclimbic_rh = _coords[10]

    # Make the PDF
    print('Making pdf')
    with PdfPages(pdf_file) as pdf:
        subject = os.path.basename(subject_dir)

        fig, ax = plt.subplots(5, 2, figsize=(8.5,11))

        fig.suptitle(f'{subject}\nDnSeg vs. sclimbic')

        # Plot the venn row
        print('Plotting venn diagrams')
        _plot_venn(volumes, ax[0])

        print('Plotting images')
        plt.subplots_adjust(
            left=0.07,
            bottom=0.07,
            right=0.93,
            top=0.93,
            wspace=0.05,
            hspace=0.15,
        )

        dnseg_lh = math_img("img == 1", img=dnseg_file)
        dnseg_rh = math_img("img == 2", img=dnseg_file)
        sclimbic_lh = math_img("img == 865", img=sclimbic_file)
        sclimbic_rh = math_img("img == 866", img=sclimbic_file)

        # Show 3 views, not zoomed with both lh
        disp = plot_roi(
            dnseg_file,
            bg_img=anat_file,
            axes=ax[1][0],
            alpha=1.0,
            title='DnSeg & sclimbic',
            cmap='gist_rainbow',
            draw_cross=False,
        )

        disp.add_overlay(sclimbic_file, cmap='tab20')

        # Show 3 views, not zoomed with both rh
        disp = plot_roi(
            dnseg_file,
            bg_img=anat_file,
            axes=ax[1][1],
            alpha=1.0,
            title='DnSeg & sclimbic',
            cmap='gist_rainbow',
            draw_cross=False,
            cut_coords=coords_dnseg_rh,
        )

        disp.add_overlay(sclimbic_file, cmap='tab20')

        # Show 3 views, zoomed with no labels lh
        disp = plot_anat(
            anat_file,
            axes=ax[2][0],
            title='ANAT',
            draw_cross=False,
            cut_coords=coords_dnseg_lh,
        )

        _zoom_ortho(disp, coords_dnseg_lh)

        # Show 3 views, zoomed with no labels rh
        disp = plot_anat(
            anat_file,
            axes=ax[2][1],
            title='ANAT',
            draw_cross=False,
            cut_coords=coords_dnseg_rh,
        )

        _zoom_ortho(disp, coords_dnseg_rh)

        # Show 3 views, zoomed with Dnseg contours lh
        disp = plot_roi(
            dnseg_lh,
            bg_img=anat_file,
            cut_coords=coords_dnseg_lh,
            axes=ax[3][0],
            alpha=1.0,
            title='NBM / BF',
            cmap='gist_rainbow',
            draw_cross=False,
            view_type='contours',
        )

        disp.add_overlay(sclimbic_lh, cmap='winter_r')

        _zoom_ortho(disp, coords_dnseg_lh)

        # Show 3 views, zoomed with DnSeg contours rh
        disp = plot_roi(
            dnseg_rh,
            bg_img=anat_file,
            cut_coords=coords_dnseg_rh,
            axes=ax[3][1],
            alpha=1.0,
            title='NBM / BF',
            cmap='spring',
            draw_cross=False,
            view_type='contours',
        )

        disp.add_overlay(sclimbic_rh, cmap='cool')

        _zoom_ortho(disp, coords_dnseg_rh)

        # Show 3 views, zoomed with sclimbic lh
        disp = plot_roi(
            sclimbic_lh,
            bg_img=anat_file,
            cut_coords=coords_sclimbic_lh,
            axes=ax[4][0],
            alpha=1.0,
            title='BF / NBM',
            cmap='winter_r',
            draw_cross=False,
            view_type='contours',
        )

        disp.add_overlay(dnseg_lh, cmap='gist_rainbow')

        _zoom_ortho(disp, coords_sclimbic_lh)

        # Show 3 views, zoomed with sclimbic rh
        disp = plot_roi(
            sclimbic_rh,
            bg_img=anat_file,
            cut_coords=coords_sclimbic_rh,
            axes=ax[4][1],
            alpha=1.0,
            title='BF / NBM',
            cmap='cool',
            draw_cross=False,
            view_type='contours',
        )

        disp.add_overlay(dnseg_rh, cmap='spring')

        _zoom_ortho(disp, coords_sclimbic_rh)

        # Save to PDF
        print(f'saving pdf:{pdf_file}')
        pdf.savefig(fig, dpi=300)

    plt.close()


def _merge_reports(reports, merged_file):
    '''Merge subject reports into a single PDF'''
    merger = PdfWriter()

    for r in reports:
        merger.append(r)

    merger.write(merged_file)
    merger.close()


def main(root_dir):
    '''Creates report per subject and summary report'''
    subj_dir = os.path.join(root_dir, 'SUBJECTS')

    print(f'Loading subjects from {subj_dir}')
    for d in sorted(os.listdir(subj_dir)):
        if d.startswith('.'):
            continue

        print(d)
        _process_subject(os.path.join(subj_dir, d))

    print('Merging subject reports')
    reports = sorted(glob(f'{subj_dir}/*/report.pdf'))
    _merge_reports(reports, f'{root_dir}/all_subject_reports.pdf')

    print('Making summary report')
    _make_summary(root_dir)


if __name__ == '__main__':
    import sys
    main(sys.argv[1])
