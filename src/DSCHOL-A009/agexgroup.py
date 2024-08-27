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
threshold_non_para = 0.005
#significance of clusters following non-parametric inference
cluster_thres = -np.log10(0.05)

#set number of permutations for non-parametric inference (10000 when finalized
# but adds compute time, 500 for running on computer)
permutations = 10000

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


#check order of covariates matches order of image imports
covariates_df['id'] = covariates_df['id'].astype(all_subs_array.dtype)
covariates_df_sorted = covariates_df.set_index('id')
covariates_df_sorted = covariates_df_sorted.loc[all_subs_array]

age_all = covariates_df_sorted['dems_age']

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


#second level model
second_level_model = SecondLevelModel(mask_img=wbmask_path, n_jobs=1).fit(
	trcds_img_paths + control_img_paths, design_matrix=design_matrix
	)

# calculate contrast
z_map = second_level_model.compute_contrast(
	second_level_contrast=[0, 0, 1, 0],
	output_type="z_score"
)


# Perform statsmap, correct for multiple comparisons
thresholded_map, threshold = threshold_stats_img(z_map, 
												 alpha=threshold_1,
												 cluster_threshold = 50)

# Save the statistical map
# Save the thresholded z-map to a NIfTI file
thresholded_map.to_filename(f'{output_path}/age_x_group_z_map.nii')

#perform glm to extract betas from age associations to understand direction
#of interaction effect

#split covariates df to DS and Control
age_ds_df = covariates_df_sorted[covariates_df_sorted['group'] == 'ds']
age_cx_df = covariates_df_sorted[covariates_df_sorted['group'] == 'control']

#select just ds or control age
design_matrix_age_ds = pd.DataFrame({
	"age": age_ds_df['dems_age'],
	"intercept": np.ones(subjects_ds)
})

design_matrix_age_control = pd.DataFrame({
	"age": age_cx_df['dems_age'],
	"intercept": np.ones(subjects_cx)
})

#calculate model ds
second_level_model_ds = SecondLevelModel(mask_img=wbmask_path, n_jobs=1).fit(
	trcds_img_paths, design_matrix=design_matrix_age_ds
	)

# calculate contrast ds and save to file
stat_map_ds = second_level_model_ds.compute_contrast(
	second_level_contrast=[1, 0],
	output_type="effect_size"
)

stat_map_ds.to_filename(f'{output_path}/ds_age_effect_size_map.nii')

#calculate model control
second_level_model_cx = SecondLevelModel(mask_img=wbmask_path, n_jobs=1).fit(
	control_img_paths, design_matrix=design_matrix_age_control
	)

# calculate contrast control and save to file
stat_map_cx = second_level_model_cx.compute_contrast(
	second_level_contrast=[1, 0],
	output_type="effect_size"
)

stat_map_cx.to_filename(f'{output_path}/control_age_effect_size_map.nii')

#perform non parametric inference
corrected_map = non_parametric_inference(
	trcds_img_paths + control_img_paths,
	design_matrix=design_matrix,
	second_level_contrast=[0, 0, 1, 0],
	mask=wbmask_path,
	n_perm=permutations,
	two_sided_test=True,
	n_jobs=1,
	threshold=threshold_non_para
	)

# extract cluster significance <0.05
img_data_non_para = corrected_map['logp_max_size'].get_fdata()
img_data_non_para[img_data_non_para < cluster_thres] = 0
img_data_non_para_mask = img_data_non_para != 0
thresholded_map_np = np.where(img_data_non_para_mask, img_data_non_para, np.nan)

thresholded_map_np_ni = new_img_like('DST3050001/smoothed_warped_FEOBV.nii.gz', thresholded_map_np)

# Save non-parametric inference corrected map
thresholded_map_np_ni.to_filename(
	f'{output_path}/Ttest_non_parametric_inference_corrected_logP_map.nii')

# Generate pdf report
pdf_filename = f"{output_path}/report.pdf"

with PdfPages(pdf_filename) as pdf:

	fig, axs = plt.subplots(3,1, figsize=(10,14))
	
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
		corrected_map['logp_max_size'],
		colorbar=True,
		vmax=-np.log10(1 / permutations),
		threshold = cluster_thres,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title = f"GLM output p < {threshold_non_para}, non-parametic inference, cluster size, p < {cluster_thres} (cluster logP)",
		axes=axs[1]
	)
	
	plotting.plot_stat_map(
		corrected_map['logp_max_mass'],
		colorbar=True,
		vmax=-np.log10(1 / permutations),
		threshold = cluster_thres,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title = "GLM output p < {threshold_non_para}, non-parametic inference, cluster mass, p < {cluster_thres} (cluster logP)",
		axes=axs[2]
	)
	
	fig.suptitle("Group x age interaction", fontsize=16,
				 weight='bold')
	
	pdf.savefig(fig, dpi=300)
	plt.close()
	
	fig, axs = plt.subplots(2,1, figsize=(10,14))
	
	plotting.plot_stat_map(
		stat_map_ds,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title = "DS age FEOBV association beta values",
		axes=axs[0]
	)
	
	plotting.plot_stat_map(
		stat_map_cx,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title = "Control age FEOBV association beta values",
		axes=axs[1]
	)
	
	fig.suptitle("Age association beta values, no threshold", fontsize=16,
				 weight='bold')
	
	pdf.savefig(fig, dpi=300)
	plt.close()
	






