from nilearn.image import math_img
from nilearn.maskers import NiftiMasker
import numpy as np
import os
from glob import glob
import pandas as pd


# garjus download -p D3 -t fmri_midt_D3_v2 -r CONN download-fmri_midt_D3_v2-CONN 
# garjus download -p D3 -t assemblynet_v1 -r DATA -f mni_structures_T1.nii.gz download-ASSEMBLYNET


#BETA_Subject001_Condition006_Source004.nii

#Source001 = Effect of Reward
#Source002 = Effect of NoReward
#Source003 = Effect of HitReward
#Source004 = Effect of MissOrNoReward
#Condition006 = Baseline

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

# Contrast 1: Effect_of_HitReward(1).Effect_of_MissOrNoReward(-1)
# Contrast 2: Effect_of_Reward(1).Effect_of_NoReward(-1)


def roi_mean(contrast_file, labels_file, label1, label2):
    print(contrast_file, labels_file, label1, label2)

    mask_image = math_img(f'(img == {label1}) | (img == {label2})', img=labels_file)
    
    masker = NiftiMasker(mask_img=mask_image).fit()

    masked = masker.fit_transform(contrast_file)

    return np.round(np.mean(masked), 6)


def extract_assr(conndir, roidir):
    data = {}
    roi_file = f'{roidir}/mni_structures_T1.nii.gz'
    reward_file = f'{conndir}/BETA_Subject001_Condition006_Source001.nii'
    noreward_file = f'{conndir}/BETA_Subject001_Condition006_Source002.nii'
    hit_file = f'{conndir}/BETA_Subject001_Condition006_Source003.nii'
    miss_file = f'{conndir}/BETA_Subject001_Condition006_Source004.nii'
    contrast1_file = f'{conndir}/contrast1.nii.gz'
    contrast2_file = f'{conndir}/contrast2.nii.gz'

    # Make contrast images
    contrast1_image = math_img("img1 - img2", img1=hit_file, img2=miss_file)
    contrast1_image.to_filename(contrast1_file)
    contrast2_image = math_img("img1 - img2", img1=reward_file, img2=noreward_file)
    contrast2_image.to_filename(contrast2_file)

    data['contrast1_caudate']  = roi_mean(contrast1_file, roi_file, 36, 37)
    data['contrast2_caudate']  = roi_mean(contrast2_file, roi_file, 36, 37)

    data['contrast1_putamen']  = roi_mean(contrast1_file, roi_file, 57, 58)
    data['contrast2_putamen']  = roi_mean(contrast2_file, roi_file, 57, 58)
    
    data['contrast1_pallidum']  = roi_mean(contrast1_file, roi_file, 55, 56)
    data['contrast2_pallidum']  = roi_mean(contrast2_file, roi_file, 55, 56)

    data['contrast1_ventraldc']  = roi_mean(contrast1_file, roi_file, 61, 62)
    data['contrast2_ventraldc']  = roi_mean(contrast2_file, roi_file, 61, 62)

    data['contrast1_midcing']  = roi_mean(contrast1_file, roi_file, 138, 139)
    data['contrast2_midcing']  = roi_mean(contrast2_file, roi_file, 138, 139)

    data['contrast1_antins']  = roi_mean(contrast1_file, roi_file, 102, 103)
    data['contrast2_antins']  = roi_mean(contrast2_file, roi_file, 102, 103)

    data['contrast1_mfc']  = roi_mean(contrast1_file, roi_file, 140, 141)
    data['contrast2_mfc']  = roi_mean(contrast2_file, roi_file, 140, 141)

    return data


if __name__ == "__main__":
    SUBJECTS_FILE = '/OUTPUTS/subjects.txt'
    PDF_NAME = '/OUTPUTS/report.pdf'
    CONNDIR = '/Users/boydb1/download-fmri_midt_D3_v2-CONN'
    ROIDIR = '/Users/boydb1/download-ASSEMBLYNET'
    CSV_FILE = '/Users/boydb1/Desktop/D3_MIDT_ROI_2026-03-10.csv'
    data = []

    assessors = [x for x in os.listdir(CONNDIR) if not x.startswith('.')]

    for i, assr in enumerate(sorted(assessors)):
        session = assr.split('-x-')[2]
        if not session.endswith('a'):
            continue

        try:
            conndir = glob(f'{CONNDIR}/*-x-{session}-x-*/CONN/conn_project/results/firstlevel/SBC_01')[0]
            roidir = glob(f'{ROIDIR}/*-x-{session}-x-*/DATA')[0]
        except:
            print('SKIPPING:incomplete', i, session, assr)
            continue

        print(i, session, assr)
        assr_data = {'PROJECT': 'D3', 'SUBJECT': session[:-1], 'SESSION': session}
        assr_data.update(extract_assr(conndir, roidir))
        data.append(assr_data)

    df = pd.DataFrame(data)
    df.to_csv(CSV_FILE, index=False)
