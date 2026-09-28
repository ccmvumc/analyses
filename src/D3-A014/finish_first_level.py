import os
from glob import glob

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from nilearn.plotting import plot_stat_map
from nilearn.datasets import fetch_atlas_schaefer_2018
from nilearn.image import load_img, math_img, new_img_like
from nilearn.maskers import NiftiMasker

from params import CUT_COORDS, COLORMAP, ROIS, TITLE, TITLE_SIZE


#BETA_Subject00X_Condition00Y_Source00Z.nii

# {SUBJECT}/conn_project/results/firstlevel/SBC_01/_list_conditions.txt 
#Condition001 = Reward 
#Condition002 = NoReward 
#Condition003 = HitReward 
#Condition004 = MissReward 
#Condition005 = MissOrNoReward 
#Condition006 = Baseline (or EndStep1)

# {SUBJECT}/conn_project/results/firstlevel/SBC_01/_list_sources.txt 
#Source001 = Effect of Reward (reward offered during Cue phase)
#Source002 = Effect of NoReward (no reward offered during Cue phase)
#Source003 = Effect of HitReward (hit reward received during Feedback phase)
#Source004 = Effect of MissOrNoReward (no reward or miss reward received during Feedback phase)

# CONTRASTS:
#
# Contrast 1: Effect_of_HitReward(1).Effect_of_MissOrNoReward(-1)
# BETA_Subject001_Condition006_Source003
# -
# BETA_Subject001_Condition006_Source004
#
# Contrast 2: Effect_of_Reward(1).Effect_of_NoReward(-1)
# BETA_Subject001_Condition006_Source001
# -
# BETA_Subject001_Condition006_Source002

#atlas_path = "/opt/to/labels_Neuromorphometrics.nii.gz"

#https://github.com/neurodebian/spm12/blob/master/tpm/labels_Neuromorphometrics.nii
# Assemblynet ROIs
#36 Right-Caudate
#37 Left-Caudate
#57 Right-Putamen
#58 Left-Putamen
#55 Right-Pallidum
#56 Left-Pallidum
#61 Right-Ventral-DC
#62 Left-Ventral-DC
#138 Right-MCgG--middle-cingulate-gyrus
#139 Left-MCgG--middle-cingulate-gyrus
#102 Right-AIns--anterior-insula
#103 Left-AIns--anterior-insula
#140 Right-MFC---medial-frontal-cortex
#141 Left-MFC---medial-frontal-cortex


def _make_roi_mask(label_file, labels, out_file):
    # Load labels
    label_image = load_img(label_file)
    label_data = label_image.get_fdata().astype(int)

    # Get ROI only
    print(labels)
    roi_data = np.isin(label_data, np.array(labels).astype(np.uint8))

    # Save to file
    print(f'writing mask file:{out_file}')
    new_img_like(label_image, roi_data).to_filename(out_file)


def _make_masks(label_dir, out_dir):
    label_file = f'{label_dir}/mni_structures_T1.nii.gz'

    _make_roi_mask(label_file, [36, 37], f'{out_dir}/caudate_mask.nii.gz')
    _make_roi_mask(label_file, [57, 58], f'{out_dir}/putamen_mask.nii.gz')
    _make_roi_mask(label_file, [55, 56], f'{out_dir}/pallidum_mask.nii.gz')
    _make_roi_mask(label_file, [61, 62], f'{out_dir}/ventraldc_mask.nii.gz')
    _make_roi_mask(label_file, [138, 139], f'{out_dir}/midcing_mask.nii.gz')
    _make_roi_mask(label_file, [102, 103], f'{out_dir}/antins_mask.nii.gz')
    _make_roi_mask(label_file, [140, 141], f'{out_dir}/mfc_mask.nii.gz')


def _roi_mean(image_file, mask_file):

    masker = NiftiMasker(mask_img=mask_file).fit()

    masked_data = masker.fit_transform(image_file)

    return np.round(np.mean(masked_data), 6)


def _contrast_images(conn_dir):
    reward_file = f'{conn_dir}/BETA_Subject001_Condition006_Source001.nii'
    noreward_file = f'{conn_dir}/BETA_Subject001_Condition006_Source002.nii'
    hit_file = f'{conn_dir}/BETA_Subject001_Condition006_Source003.nii'
    miss_file = f'{conn_dir}/BETA_Subject001_Condition006_Source004.nii'
    contrast1_file = f'{conn_dir}/contrast1.nii.gz'
    contrast2_file = f'{conn_dir}/contrast2.nii.gz'

    # Make contrast images
    contrast1_image = math_img("img1 - img2", img1=hit_file, img2=miss_file)
    contrast1_image.to_filename(contrast1_file)
    contrast2_image = math_img("img1 - img2", img1=reward_file, img2=noreward_file)
    contrast2_image.to_filename(contrast2_file)


def _extract_rois(conn_dir, roi_dir):
    data = {}
    contrast1_file = f'{conn_dir}/contrast1.nii.gz'
    contrast2_file = f'{conn_dir}/contrast2.nii.gz'
    masks = glob(f'{roi_dir}/*.nii.gz')

    # Extract mean of contrast per ROI
    for m in masks:
        r = os.path.basename(m).split('_mask.nii.gz')[0]
        data[f'contrast1_{r}']  = _roi_mean(contrast1_file, m)
        data[f'contrast2_{r}']  = _roi_mean(contrast2_file, m)

    return data


def _plot_contrasts(conn_dir, roi_dir):
    subj = conn_dir.split('/')[-5]

    # Make a letter paper size figure with 6 plots in 1 column
    fig, ax = plt.subplots(2, 1, figsize=(8.5,11))

    for i, c in enumerate(['contrast1', 'contrast2']):

        display = plot_stat_map(
            f'{conn_dir}/{c}.nii.gz',
            display_mode='z',
            cut_coords=CUT_COORDS,
            cmap=COLORMAP,
            vmax=0.5,
            axes=ax[i],
        )

        display.title(
            f'{TITLE} 1st-Level contrast:{c}:{subj}',
            size=TITLE_SIZE
        )

        # Trace ROI outline
        for r in glob(f'{roi_dir}/*.nii.gz'):
            display.add_contours(r, levels=[0.5], colors="g")

    # Save plot
    plt.savefig(f'{conn_dir}/contrast_report.pdf')

    plt.close()


def _write_subjects(subjects, filename):
    '''Writes a text file with one subject per line'''
    with open(filename, 'w') as f:
        f.write('\n'.join(subjects) + '\n')


def main(input_dir, output_dir):
    include_subjects = []
    data = []
    csv_file = f'{output_dir}/roi_means.csv'

    print('loading subjects')
    subjects = sorted([x for x in os.listdir(input_dir) if os.path.isdir(f'{input_dir}/{x}')])
    print(subjects)

    # Run each subject
    for i, subj in enumerate(subjects):

        sessions = [x for x in os.listdir(f'{input_dir}/{subj}') if os.path.isdir(f'{input_dir}/{subj}/{x}')]
        print(sessions)

        for sess in sorted(sessions):
            sess_dir = f'{output_dir}/{subj}/{sess}'
            print(sess_dir)

            try:
                conn_dir = glob(f'{output_dir}/SUBJECTS/{subj}/{sess}/conn_project/results/firstlevel/SBC_01')[0]
                print(f'{conn_dir=}')
            except:
                print('SKIPPING:incomplete', i, subj)
                continue

            try:
                label_dir = glob(f'{input_dir}/{subj}/{sess}/assessors/*assemblynet*')[0]
                print(f'{label_dir=}')
            except:
                print('SKIPPING:incomplete', i, subj, sess)
                continue

            include_subjects.append(subj)

            print(f'Running:{subj}:{sess}')

            print(f'{subj}:{sess}:making masks')
            roi_dir = f'{conn_dir}/ROIS'
            os.makedirs(roi_dir, exist_ok=True)
            _make_masks(label_dir, roi_dir)

            print(f'{subj}:{sess}:making contrasts')
            _contrast_images(conn_dir)

            print(f'{subj}:{sess}:plotting contrasts')
            _plot_contrasts(conn_dir, roi_dir)

            print(f'{subj}:{sess}:extracting ROIs')
            data.append(_extract_rois(conn_dir, roi_dir))

    # Save ROI data
    df = pd.DataFrame(data)
    print(f'saving to file:{csv_file}')
    print(df)
    df.to_csv(csv_file, index=False)

    # Save subject list
    _write_subjects(include_subjects, f'{output_dir}/subjects.txt')


if __name__ == '__main__':
    import sys

    # input dir
    # output dir
    main(sys.argv[1], sys.argv[2])
