#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 12:59:50 2024

@author: jason
"""

from nilearn import image
from nilearn.glm.second_level import SecondLevelModel
from nilearn.glm import threshold_stats_img
import pandas as pd
import os
import numpy as np
from nilearn import plotting
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from nilearn.glm.second_level import non_parametric_inference
from nilearn.image import new_img_like
import glob

#image paths - split data to make counts easier later
trcds_img_paths = (glob.glob('/OUTPUTS/DATA/DST*/smoothed_warped_FEOBV.nii.gz') + 
				   glob.glob('/OUTPUTS/DATA/DSCHOL*/smoothed_warped_FEOBV.nii.gz')
				   )

trcds_img_paths = sorted(trcds_img_paths)

control_img_paths = (glob.glob('/OUTPUTS/DATA/Sub*/smoothed_warped_FEOBV.nii.gz') + 
				   glob.glob('/OUTPUTS/DATA/2*/smoothed_warped_FEOBV.nii.gz')
				   )

control_img_paths = sorted(control_img_paths)

print("Data paths for t-test groups set")

#Set path where data is stored
data_path = '/OUTPUTS/DATA'

os.chdir(data_path)

#generate subject list in order of import
subject_list_trcds=[]

for subject in trcds_img_paths:
	path = os.path.normpath(subject)
	trcds_parts = path.split(os.sep)
	sub_id = trcds_parts[-2]
	subject_list_trcds.append(sub_id)
	
print(f'DS subject order: {subject_list_trcds}')

subject_list_control=[]


for subject in control_img_paths:
	path = os.path.normpath(subject)
	control_parts = path.split(os.sep)
	sub_id = control_parts[-2]
	subject_list_control.append(sub_id)
	
print(f'Control subject order: {subject_list_control}')
all_subs = subject_list_trcds + subject_list_control

all_subs_array = np.array(all_subs)

#set signficant thresholds for different tests
#significance (p-val) for initial test at cluster threshold 50
threshold_1 = 0.001
#fdr threshold
fdr_threshold = 0.05

# Load the study-specific whole brain mask 
wbmask_path = 'Brain_mask_prob0_3.nii'


# Load DS images to 4D nifti
trcds_img = image.concat_imgs(trcds_img_paths)

# Load Control images to 4d nifti
control_img = image.concat_imgs(control_img_paths)


# Count subjects for each group
_, _, _, subjects_ds = trcds_img.shape
_, _, _, subjects_cx = control_img.shape

#import sex variables and check order matches order of image imports
sex_df = pd.read_csv('/INPUTS/covariates.csv')
sex_df['id'] = sex_df['id'].astype(all_subs_array.dtype)
sex_df_sorted = sex_df.set_index('id')
sex_df_sorted = sex_df_sorted.loc[all_subs_array]

sex_all, sex_all_key = pd.factorize(sex_df_sorted['dems_sex'])
age = sex_df_sorted['dems_age'].astype(float)

print("Covariates loaded")
print(sex_df_sorted)


# Generate design matrix
unpaired_design_matrix = pd.DataFrame({
	"Down Syndrome": np.concatenate([np.ones(subjects_ds), np.zeros(subjects_cx)]),
	"Intercept:": np.ones(subjects_ds + subjects_cx)
})

# second level model
second_level_model = SecondLevelModel(mask_img=wbmask_path, n_jobs=1).fit(
	trcds_img_paths + control_img_paths, design_matrix=unpaired_design_matrix
	)

# calculate contrast
t_map = second_level_model.compute_contrast(
	second_level_contrast=[1, 0],
	second_level_stat_type='t',
	output_type="stat",
)

# Perform statsmap, correct for multiple comparisons
thresholded_map, threshold = threshold_stats_img(t_map,
												 alpha=threshold_1,
												 cluster_threshold=50)

print(f't-score threshold:{threshold}')

# Save the thresholded t-map to a NIfTI file
thresholded_map.to_filename(
	'thresholded_groupwise_comparison_t_map.nii')

#repeat with fdr correction
thresholded_map_fdr, threshold_fdr = threshold_stats_img(
    t_map, alpha=fdr_threshold, height_control="fdr"
)

print(f'fdr corrected t-score threshold:{threshold_fdr}')

thresholded_map_fdr.to_filename(
	'fdr_thresholded_groupwise_comparison_t_map.nii')


# Generate pdf report
pdf_filename = "/OUTPUTS/report.pdf"


with PdfPages(pdf_filename) as pdf:

	fig, axs = plt.subplots(2,1, figsize=(10,14))
	
	plotting.plot_stat_map(
		thresholded_map,
		threshold=threshold,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title = f"Threshold t-scores p < {threshold_1}, cluster size 50 (t-score thres: {threshold})",
		axes=axs[0]
	)
	
	plotting.plot_stat_map(
		thresholded_map_fdr,
		threshold=threshold_fdr,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title = f"FDR-corrected threshold t-scores p < {fdr_threshold}, cluster size 50 (z-scores)",
		axes=axs[1]
	)
	

