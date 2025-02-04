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
from config import out_dir, covariates

#Set path where data is stored
data_path = out_dir

os.chdir(data_path)
output_path = out_dir

#set signficant thresholds for different tests
#significance (p-val) for initial test at cluster threshold 50
threshold_1 = 0.005
threshold_non_para = 0.005
#significance of clusters following non-parametric inference
cluster_thres = -np.log10(0.05)
fdr_thres = 0.05

#set number of permutations for non-parametric inference (10000 when finalized
# but adds compute time, 500 for running on computer)
permutations = 50

#import covariates
covariates_df = pd.read_csv(f'{covariates}/covariates.csv')

# Load the study-specific whole brain mask
wbmask_path = 'Brain_mask_prob0_3.nii'

# Load PET images
# DS data image paths
trcds_img_paths = (glob.glob(f'{out_dir}/DST*/smoothed_warped_FEOBV.nii.gz') +
				   glob.glob(f'{out_dir}/DSCHOL*/smoothed_warped_FEOBV.nii.gz')
				   )

trcds_img_paths = sorted(trcds_img_paths)

# Control cohort image paths
control_img_paths = (
				   glob.glob(f'{out_dir}/2*/smoothed_warped_FEOBV.nii.gz')
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

centiloid_all = covariates_df_sorted['Centiloid']
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
interaction = DS * centiloid_all

design_matrix = pd.DataFrame({
	"Down Syndrome": DS,
	"Centiloid":centiloid_all,
	"Interaction": interaction,
	"Intercept": np.ones(subjects_ds + subjects_cx)
})

design_matrix_age = pd.DataFrame({
	"Down Syndrome": DS,
	"Centiloid":centiloid_all,
	"Interaction": interaction,
	"Age": age_all,
	"Intercept": np.ones(subjects_ds + subjects_cx)
})


#second level model
second_level_model = SecondLevelModel(mask_img=wbmask_path, n_jobs=1).fit(
	trcds_img_paths + control_img_paths, design_matrix=design_matrix
	)

second_level_model_age = SecondLevelModel(mask_img=wbmask_path, n_jobs=1).fit(
	trcds_img_paths + control_img_paths, design_matrix=design_matrix_age
	)


# calculate contrast
z_map = second_level_model.compute_contrast(
	second_level_contrast=[0, 0, 1, 0],
	output_type="z_score"
)

z_map_age = second_level_model_age.compute_contrast(
	second_level_contrast=[0, 0, 1, 0, 0],
	output_type="z_score"
)


# Perform statsmap, correct for multiple comparisons
thresholded_map, threshold = threshold_stats_img(z_map, 
												 alpha=threshold_1,
												 cluster_threshold = 50)

thresholded_map_fdr, threshold_fdr = threshold_stats_img(z_map,
														 alpha=fdr_thres,
														 height_control= 'fdr')

thresholded_map_age, threshold_age = threshold_stats_img(z_map_age,
												 alpha=threshold_1,
												 cluster_threshold = 50)

thresholded_map_age_fdr, threshold_age_fdr = threshold_stats_img(z_map_age,
																 alpha=fdr_thres,
																 height_control= 'fdr')

# Save the statistical map
# Save the thresholded z-map to a NIfTI file
thresholded_map.to_filename(f'{output_path}/centiloid_x_group_z_map.nii')

thresholded_map_fdr.to_filename(f'{output_path}/centiloid_x_group_z_map_fdr_corrected.nii')

thresholded_map_age.to_filename(f'{output_path}/centiloid_x_group_age_z_map.nii')

thresholded_map_age_fdr.to_filename(f'{output_path}/centiloid_x_group_age_z_map_fdr_corrected.nii')

#perform glm to extract betas from centiloid associations to understand direction
#of interaction effect

#split covariates df to DS and Control
cov_ds_df = covariates_df_sorted[covariates_df_sorted['group'] == 'ds']
cov_cx_df = covariates_df_sorted[covariates_df_sorted['group'] == 'control']

#select just ds or control centiloid
design_matrix_centiloid_ds = pd.DataFrame({
	"centiloid": cov_ds_df['Centiloid'],
	"intercept": np.ones(subjects_ds)
})

design_matrix_centiloid_ds_age = pd.DataFrame({
	"centiloid": cov_ds_df['Centiloid'],
	"age": cov_ds_df['dems_age'],
	"intercept": np.ones(subjects_ds)
})

design_matrix_centiloid_control = pd.DataFrame({
	"centiloid": cov_cx_df['Centiloid'],
	"intercept": np.ones(subjects_cx)
})

design_matrix_centiloid_control_age = pd.DataFrame({
	"centiloid": cov_cx_df['Centiloid'],
	"age": cov_cx_df['dems_age'],
	"intercept": np.ones(subjects_cx)
})


#calculate model ds
second_level_model_ds = SecondLevelModel(mask_img=wbmask_path, n_jobs=1).fit(
	trcds_img_paths, design_matrix=design_matrix_centiloid_ds
	)

second_level_model_ds_age = SecondLevelModel(mask_img=wbmask_path, n_jobs=1).fit(
	trcds_img_paths, design_matrix=design_matrix_centiloid_ds_age
	)

# calculate contrast ds and save to file
stat_map_ds = second_level_model_ds.compute_contrast(
	second_level_contrast=[1, 0],
	output_type="effect_size"
)

stat_map_ds_age = second_level_model_ds_age.compute_contrast(
	second_level_contrast=[1, 0, 0],
	output_type="effect_size"
)

stat_map_ds.to_filename(f'{output_path}/ds_centiloid_effect_size_map.nii')
stat_map_ds_age.to_filename(f'{output_path}/ds_centiloid_age_effect_size_map.nii')

#calculate model control
second_level_model_cx = SecondLevelModel(mask_img=wbmask_path, n_jobs=1).fit(
	control_img_paths, design_matrix=design_matrix_centiloid_control
	)

second_level_model_cx_age = SecondLevelModel(mask_img=wbmask_path, n_jobs=1).fit(
	control_img_paths, design_matrix=design_matrix_centiloid_control_age
	)


# calculate contrast control and save to file
stat_map_cx = second_level_model_cx.compute_contrast(
	second_level_contrast=[1, 0],
	output_type="effect_size"
)

stat_map_cx_age = second_level_model_cx_age.compute_contrast(
	second_level_contrast=[1, 0, 0],
	output_type="effect_size"
)

stat_map_cx.to_filename(f'{output_path}/control_centiloid_effect_size_map.nii')
stat_map_cx_age.to_filename(f'{output_path}/control_centiloid_age_effect_size_map.nii')

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
	f'{output_path}/interact_non_parametric_inference_corrected_logP_map.nii')

# Generate pdf report
pdf_filename = "OUTPUTS/report.pdf"

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
		threshold=fdr_thres,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title = f"GLM output p < {fdr_thres}, FDR corrected",
		axes=axs[1]
	)
	
	fig.suptitle("Group x centiloid interaction", fontsize=16,
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
		title = "DS centiloid FEOBV association beta values",
		axes=axs[0]
	)
	
	plotting.plot_stat_map(
		stat_map_cx,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title = "Control centiloid FEOBV association beta values",
		axes=axs[1]
	)
	
	fig.suptitle("Centiloid association beta values, no threshold", fontsize=16,
				 weight='bold')
	
	pdf.savefig(fig, dpi=300)
	plt.close()

	fig, axs = plt.subplots(2, 1, figsize=(10, 14))

	plotting.plot_stat_map(
		thresholded_map_age,
		threshold=threshold_1,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title=f"GLM output, age corrected, p < {threshold_1}, cluster size 50 (z-scores)",
		axes=axs[0]
	)

	plotting.plot_stat_map(
		thresholded_map_age_fdr,
		threshold=fdr_thres,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title=f"GLM output, age corrected, p < {fdr_thres}, FDR corrected",
		axes=axs[1]
	)

	fig.suptitle("Group x centiloid interaction age as covariate", fontsize=16,
				 weight='bold')

	pdf.savefig(fig, dpi=300)
	plt.close()

	fig, axs = plt.subplots(2, 1, figsize=(10, 14))

	plotting.plot_stat_map(
		stat_map_ds_age,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title="DS centiloid FEOBV association age corrected beta values",
		axes=axs[0]
	)

	plotting.plot_stat_map(
		stat_map_cx_age,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title="Control centiloid FEOBV association age corrected beta values",
		axes=axs[1]
	)

	fig.suptitle("Centiloid association beta values, no threshold, age as covariate", fontsize=16,
				 weight='bold')

	pdf.savefig(fig, dpi=300)
	plt.close()
	






