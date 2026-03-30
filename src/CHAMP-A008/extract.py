import os
from glob import glob

import numpy as np
import pandas as pd
from nilearn.image import load_img, math_img, new_img_like
from nilearn.datasets import fetch_atlas_schaefer_2018
from nilearn.masking import apply_mask


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


# Regions of interest for extraction
ROIS = [
    {
        'name': 'dlpfc',
        'atlas': 'Schaefer200',
        'labels': [66, 67, 68, 69, 70, 170, 171, 172, 173, 174, 175, 176]
    },
    {
        'name': 'ppc',
        'atlas': 'Schaefer200',
        'labels': [61, 62, 63, 165, 166, 167]
    },
]


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


def extract_assr(conndir, roidir):
    data = {}
    mec_0back_file = f'{conndir}/BETA_Subject001_Condition005_Source001.nii'
    mec_2back_file = f'{conndir}/BETA_Subject001_Condition005_Source003.nii'
    plc_0back_file = f'{conndir}/BETA_Subject001_Condition006_Source001.nii'
    plc_2back_file = f'{conndir}/BETA_Subject001_Condition006_Source003.nii'
    mec_contrast1_file = f'{conndir}/mec_contrast1.nii.gz'
    plc_contrast1_file = f'{conndir}/plc_contrast1.nii.gz'
    masks = glob(f'{roidir}/*.nii.gz')

    # Make contrast images
    mec_contrast1_image = math_img(
        "img1 - img2",
        img1=mec_2back_file,
        img2=mec_0back_file,
    )
    mec_contrast1_image.to_filename(mec_contrast1_file)

    plc_contrast1_image = math_img(
        "img1 - img2",
        img1=plc_2back_file,
        img2=plc_0back_file,
    )
    plc_contrast1_image.to_filename(plc_contrast1_file)

    # Extract mean of contrast per ROI
    for m in masks:
        r = os.path.basename(m).split('_mask.nii.gz')[0]
        data[f'mec_contrast1_{r}']  = _roi_mean(mec_contrast1_file, m)
        data[f'plc_contrast1_{r}']  = _roi_mean(plc_contrast1_file, m)

    return data


def main(output_dir):
    csv_file = os.path.join(output_dir, 'roi_means.csv')
    roi_dir = f'{output_dir}/ROIS'
    data = []
    subjects = [x for x in os.listdir(output_dir) if not x.startswith('.')]

    print('making masks')
    os.makedirs(roi_dir, exist_ok=True)
    _make_roi_masks(roi_dir, ROIS)

    for i, subj in enumerate(sorted(subjects)):
        try:
            conndir = glob(f'{output_dir}/{subj}/conn_project/results/firstlevel/SBC_01')[0]
        except:
            print('SKIPPING:incomplete', i, subj)
            continue

        print(i, subj)
        subj_data = {'PROJECT': 'CHAMP', 'SUBJECT': subj}
        subj_data.update(extract_assr(conndir, roi_dir))
        data.append(subj_data)

    df = pd.DataFrame(data)
    print(f'saving to file:{csv_file}')
    df.to_csv(csv_file, index=False)


if __name__ == "__main__":
    ROOTDIR = '/Users/brian/TEST-CHAMP-A008/OUTPUTS'
    main(ROOTDIR)
