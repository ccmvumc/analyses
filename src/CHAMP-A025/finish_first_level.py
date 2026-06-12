import os
from glob import glob

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from nilearn.plotting import plot_stat_map
from nilearn.datasets import fetch_atlas_schaefer_2018
from nilearn.image import load_img, math_img, new_img_like
from nilearn.masking import apply_mask

from params import CUT_COORDS, COLORMAP, ROIS


TITLE='CHAMP N-Back Task'


#BETA_Subject00X_Condition00Y_Source00Z.nii

# {SUBJECT}/conn_project/results/firstlevel/SBC_01/_list_conditions.txt 
#Condition001 = 0Back
#Condition002 = 1Back
#Condition003 = 2Back
#Condition004 = 3Back
#Condition005 = MEC
#Condition006 = PLC

# {SUBJECT}/conn_project/results/firstlevel/SBC_01/_list_sources.txt 
#Source001 = Effect of 0Back
#Source002 = Effect of 1Back
#Source003 = Effect of 2Back
#Source004 = Effect of 3Back

# Contrast 1: (MEC.2Back - MEC.0Back) - (PLC.2Back - PLC.0Back)
# Contrast 1: 
#  (
#    BETA_Subject001_Condition005_Source003.nii
#    - 
#    BETA_Subject001_Condition005_Source001.nii
#  ) 
#  -
#  (
#    BETA_Subject001_Condition006_Source003.nii 
#    -
#    BETA_Subject001_Condition006_Source001.nii
#  )


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


def _roi_mean(image, mask):
    masked_data = apply_mask(image, mask)
    return np.round(np.mean(masked_data), 6)


def _contrast_images(conn_dir):
    mec_0back_file = f'{conn_dir}/BETA_Subject001_Condition005_Source001.nii'
    mec_2back_file = f'{conn_dir}/BETA_Subject001_Condition005_Source003.nii'
    plc_0back_file = f'{conn_dir}/BETA_Subject001_Condition006_Source001.nii'
    plc_2back_file = f'{conn_dir}/BETA_Subject001_Condition006_Source003.nii'
    mec_contrast1_file = f'{conn_dir}/mec_contrast1.nii.gz'
    plc_contrast1_file = f'{conn_dir}/plc_contrast1.nii.gz'

    # Make contrast images
    mec_contrast1_image = math_img(
        "img1 - img2",
        img1=mec_2back_file,
        img2=mec_0back_file,
    )
    print(f'Saving MEC contrast1:{mec_contrast1_file}')
    mec_contrast1_image.to_filename(mec_contrast1_file)

    plc_contrast1_image = math_img(
        "img1 - img2",
        img1=plc_2back_file,
        img2=plc_0back_file,
    )
    print(f'Saving PLC contrast1:{plc_contrast1_file}')
    plc_contrast1_image.to_filename(plc_contrast1_file)


def _extract_rois(conn_dir, roi_dir):
    data = {}
    mec_contrast1_file = f'{conn_dir}/mec_contrast1.nii.gz'
    plc_contrast1_file = f'{conn_dir}/plc_contrast1.nii.gz'
    masks = glob(f'{roi_dir}/*.nii.gz')

    # Extract mean of contrast per ROI
    for m in masks:
        r = os.path.basename(m).split('_mask.nii.gz')[0]
        data[f'mec_contrast1_{r}']  = _roi_mean(mec_contrast1_file, m)
        data[f'plc_contrast1_{r}']  = _roi_mean(plc_contrast1_file, m)

    return data


def _plot_contrasts(conn_dir, roi_dir):
    subj = conn_dir.split('/')[-5]

    for sess in ['mec', 'plc']:
        display = plot_stat_map(
            f'{conn_dir}/{sess}_contrast1.nii.gz',
            threshold=0.05,
            display_mode='z',
            cut_coords=CUT_COORDS,
            title=f'{TITLE} 1st-Level contrast:{sess}:{subj}',
            cmap=COLORMAP,
            vmax=1.0,
        )

        # Trace ROI outline
        for r in glob(f'{roi_dir}/*.nii.gz'):
            display.add_contours(r, levels=[0.5], colors="g")

        # Save plot
        plt.savefig(f'{conn_dir}/{sess}_contrast1_report.pdf')

        plt.close()


def _write_subjects(subjects, filename):
    '''Writes a text file with one subject per line'''
    with open(filename, 'w') as f:
        f.write('\n'.join(subjects) + '\n')


def main(input_dir, output_dir):
    include_subjects = []
    data = []
    roi_dir = f'{output_dir}/ROIS'
    csv_file = f'{output_dir}/roi_means.csv'

    print('making masks')
    os.makedirs(roi_dir, exist_ok=True)
    _make_roi_masks(roi_dir, ROIS)

    print('loading subjects')
    subjects = sorted([x for x in os.listdir(input_dir) if os.path.isdir(f'{input_dir}/{x}')])
    print(subjects)

    # Run each subject
    for i, subj in enumerate(subjects):
        try:
            conn_dir = glob(f'{output_dir}/SUBJECTS/{subj}/conn_project/results/firstlevel/SBC_01')[0]
        except:
            print('SKIPPING:incomplete', i, subj)
            continue

        include_subjects.append(subj)

        print(f'Running:{subj}')
        _contrast_images(conn_dir)
        _plot_contrasts(conn_dir, roi_dir)
        data.append(_extract_rois(conn_dir, roi_dir))

    # Save ROI data
    df = pd.DataFrame(data)
    print(f'saving to file:{csv_file}')
    print(df)
    df.to_csv(csv_file, index=False)

    # Save subject list
    _write_subjects(include_subjects, '/OUTPUTS/subjects.txt')



if __name__ == '__main__':
    import sys

    main(sys.argv[1], sys.argv[2])
