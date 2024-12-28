#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 14:06:35 2024

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

#Set path where data is stored
data_path = '/OUTPUTS/DATA'

os.chdir(data_path)
output_path = '/OUTPUTS/DATA'

#set signficant thresholds for different tests
#significance (p-val) for initial test at cluster threshold 50
threshold_1 = 0.005
#fdr threshold
fdr_threshold = 0.05

#import age
covariates_df = pd.read_csv('/INPUTS/covariates.csv')

# Load the study-specific whole brain mask
wbmask_path = 'Brain_mask_prob0_3.nii'

# Load PET images
# DS data image paths
trcds_img_paths = (glob.glob('/OUTPUTS/DATA/DST*/smoothed_warped_FEOBV.nii.gz') + 
				   glob.glob('/OUTPUTS/DATA/DSCHOL*/smoothed_warped_FEOBV.nii.gz')
				   )

trcds_img_paths = sorted(trcds_img_paths)

# Control cohort image paths
control_img_paths = (glob.glob('/OUTPUTS/DATA/Sub*/smoothed_warped_FEOBV.nii.gz') + 
				   glob.glob('/OUTPUTS/DATA/1*/smoothed_warped_FEOBV.nii.gz')
				   )

control_img_paths = sorted(control_img_paths)

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

print(f'All Subjects: {all_subs_array}')


#check order of covariates matches order of image imports
covariates_df['id'] = covariates_df['id'].astype(all_subs_array.dtype)
covariates_df_sorted = covariates_df.set_index('id')
covariates_df_sorted = covariates_df_sorted.loc[all_subs_array]

age_all = covariates_df_sorted['dems_age']
sex_all = covariates_df_sorted['dems_sex']

print(f'Covariates dataframe: {covariates_df_sorted}')

sex_fact, sex_fact_key = pd.factorize(sex_all)

# Load DS images to 4D nifti
trcds_img = image.concat_imgs(trcds_img_paths)

# Load Control images to 4d nifti
control_img = image.concat_imgs(control_img_paths)

# Count subjects for each group
_, _, _, subjects_ds = trcds_img.shape
_, _, _, subjects_cx = control_img.shape

# Generate design matrix
DS = np.concatenate([np.ones(subjects_ds), np.zeros(subjects_cx)])
interaction = DS * age_all

design_matrix = pd.DataFrame({
	"Down Syndrome": DS,
	"Age":age_all,
	"Interaction": interaction,
	"Intercept": np.ones(subjects_ds + subjects_cx)
})

print(f'Design Matrix: {design_matrix}')


# design_matrix_sex = pd.DataFrame({
# 	"Down Syndrome": DS,
# 	"Age":age_all,
# 	"Interaction": interaction,
# 	"Sex": sex_fact,
# 	"Intercept": np.ones(subjects_ds + subjects_cx)
# })

# print(f'Design Matrix (sex controlled): {design_matrix_sex}')

all_subjects_paths = trcds_img_paths + control_img_paths

print(f'Order of all subjects image paths: {all_subjects_paths}')


#second level model
second_level_model = SecondLevelModel(mask_img=wbmask_path, n_jobs=1).fit(
	all_subjects_paths, design_matrix=design_matrix
	)
#
# second_level_model_sex = SecondLevelModel(mask_img=wbmask_path, n_jobs=1).fit(
# 	all_subjects_paths, design_matrix=design_matrix_sex
# 	)

# calculate contrast
z_map = second_level_model.compute_contrast(
	second_level_contrast=[0, 0, 1, 0],
	output_type="z_score"
)

# z_map_sex = second_level_model_sex.compute_contrast(
# 	second_level_contrast=[0, 0, 1, 0, 0],
# 	output_type="z_score"
# )


# Perform statsmap, correct for multiple comparisons
thresholded_map, threshold = threshold_stats_img(z_map, 
												 alpha=threshold_1,
												 cluster_threshold = 50)

#fdr correction
thresholded_map_fdr, threshold_fdr = threshold_stats_img(z_map,
												 alpha=fdr_threshold, height_control="fdr"
												 )

# thresholded_map_sex, threshold_sex = threshold_stats_img(z_map_sex,
# 												 alpha=threshold_1,
# 												 cluster_threshold = 50)

# Save the statistical map
# Save the thresholded z-map to a NIfTI file
thresholded_map.to_filename(f'{output_path}/age_x_group_z_map.nii')
thresholded_map_fdr.to_filename(f'{output_path}/fdr_age_x_group_z_map.nii')

#thresholded_map_sex.to_filename(f'{output_path}/age_x_group_sex_covariate_z_map.nii')


# Generate pdf report
pdf_filename = "/OUTPUTS/report.pdf"

with PdfPages(pdf_filename) as pdf:

	fig, axs = plt.subplots(2,1, figsize=(10,14))
	
	plotting.plot_stat_map(
		thresholded_map,
		threshold=threshold_1,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title = f"GLM output p < {threshold_1}, cluster size 50 (z-scores)",
		axes=axs[0]
	)
	plotting.plot_stat_map(
		thresholded_map_fdr,
		threshold=threshold_fdr,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title = f"FDR corrected GLM output p < {fdr_threshold} (Threshold: {threshold_fdr})",
		axes=axs[1]
	)
	
	pdf.savefig(fig, dpi=300)
	plt.close()





