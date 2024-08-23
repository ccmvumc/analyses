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

control_img_paths = (glob.glob('/OUTPUTS/DATA/Sub*/smoothed_warped_FEOBV.nii.gz') + 
				   glob.glob('/OUTPUTS/DATA/1*/smoothed_warped_FEOBV.nii.gz')
				   )

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
control_parts = trcds_img_paths.split(os.sep)

for subject in control_img_paths:
	sub_id = trcds_parts[-2]
	subject_list_control.append(sub_id)
	
print(f'Control subject order: {subject_list_control}')
all_subs = subject_list_trcds + subject_list_control

all_subs_array = np.array(all_subs)

#set signficant thresholds for different tests
#significance (p-val) for initial test at cluster threshold 50
threshold_1 = 0.005
#significance for voxel-level significance, non-paramteric inference
threshold_non_para = 0.005
#significance of clusters following non-parametric inference
cluster_thres = -np.log10(0.05)

#set number of permutations for non-parametric inference (10000 when finalized
# but adds compute time, 500 for running on computer)
permutations = 10000

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
sex_df = pd.read_csv('covariates.csv')
sex_df['id'] = sex_df['id'].astype(all_subs_array.dtype)
sex_df_sorted = sex_df.set_index('id')
sex_df_sorted = sex_df_sorted.loc[all_subs_array]

sex_all, sex_all_key = pd.factorize(sex_df_sorted['dems_sex'])

print("Covariates loaded")


# Generate design matrix control for sex 
unpaired_design_matrix_sex = pd.DataFrame({
	"Down Syndrome": np.concatenate([np.ones(subjects_ds), np.zeros(subjects_cx)]),
	"Sex": sex_all,
	"Intercept:": np.ones(subjects_ds + subjects_cx)
})

# second level model
second_level_model = SecondLevelModel(mask_img=wbmask_path, n_jobs=1).fit(
	trcds_img_paths + control_img_paths, design_matrix=unpaired_design_matrix_sex
	)

# calculate contrast
z_map = second_level_model.compute_contrast(
	second_level_contrast=[1, 0, 0],
	output_type="z_score",
)

# Perform statsmap, correct for multiple comparisons
thresholded_map_sex, threshold_sex = threshold_stats_img(z_map, 
												 alpha=threshold_1,
												 cluster_threshold=50)

# Save the thresholded z-map to a NIfTI file
thresholded_map_sex.to_filename(
	'thresholded_groupwise_comparison_z_map_sex_corrected.nii')

#perform non parametric inference
corrected_map_sex = non_parametric_inference(
	trcds_img_paths + control_img_paths,
	design_matrix=unpaired_design_matrix_sex,
	second_level_contrast=[1,0,0],
	mask=wbmask_path,
	n_perm=permutations,
	two_sided_test=True,
	n_jobs=1,
	threshold=threshold_non_para
	)

# extract cluster significance <0.05
img_data_non_para_sex = corrected_map_sex['logp_max_size'].get_fdata()
img_data_non_para_sex[img_data_non_para_sex < cluster_thres] = 0
img_data_non_para_mask_sex = img_data_non_para_sex != 0
thresholded_map_np_sex = np.where(img_data_non_para_mask_sex, img_data_non_para_sex, np.nan)

thresholded_map_np_sex_ni = new_img_like(
	'DST3050001/smoothed_warped_FEOBV.nii.gz', 
	thresholded_map_np_sex
	)

# Save non-parametric inference corrected map
thresholded_map_np_sex_ni.to_filename(
	'Ttest_non_parametric_inference_corrected_sex_control_logP_map.nii')



#repeat t-test without controlling for sex
# Generate design matrix control for sex 
unpaired_design_matrix = pd.DataFrame({
	"Down Syndrome": np.concatenate([np.ones(subjects_ds), np.zeros(subjects_cx)]),
})

# second level model
second_level_model = SecondLevelModel(mask_img=wbmask_path, n_jobs=1).fit(
	trcds_img_paths + control_img_paths, design_matrix=unpaired_design_matrix
	)

# calculate contrast
z_map = second_level_model.compute_contrast(
	"Down Syndrome",
	output_type="z_score",
)

# Perform statsmap, correct for multiple comparisons
thresholded_map, threshold = threshold_stats_img(z_map, 
												 alpha=threshold_1,
												 cluster_threshold=50)

# Save the thresholded z-map to a NIfTI file
thresholded_map.to_filename(
	'thresholded_groupwise_comparison_z_map.nii')

#perform non parametric inference
corrected_map = non_parametric_inference(
	trcds_img_paths + control_img_paths,
	design_matrix=unpaired_design_matrix,
	second_level_contrast=[1],
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

thresholded_map_np_ni = new_img_like(
	'DST3050001/smoothed_warped_FEOBV.nii.gz', thresholded_map_np)

# Save non-parametric inference corrected map
thresholded_map_np_ni.to_filename(
	'Ttest_non_parametric_inference_corrected_logP_map.nii')

# Generate pdf report
pdf_filename = "Groupwise T-test FEOBV.pdf"

with PdfPages(pdf_filename) as pdf:

	fig, axs = plt.subplots(3,1, figsize=(10,14))
	
	plotting.plot_stat_map(
		thresholded_map_sex,
		threshold=threshold_1,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title = "GLM output p < 0.005, cluster size 50 (z-scores)",
		axes=axs[0]
	)
	
	plotting.plot_stat_map(
		corrected_map_sex['logp_max_size'],
		colorbar=True,
		vmax=-np.log10(1 / permutations),
		threshold = cluster_thres,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title = "GLM output p < 0.005, non-parametic inference, cluster size (cluster logP)",
		axes=axs[1]
	)
	
	plotting.plot_stat_map(
		corrected_map_sex['logp_max_mass'],
		colorbar=True,
		vmax=-np.log10(1 / permutations),
		threshold = cluster_thres,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title = "GLM output p < 0.005, non-parametic inference, cluster mass (cluster logP)",
		axes=axs[2]
	)
	
	fig.suptitle("Groupwise T-test adjusting for Sex", fontsize=16,
				 weight='bold')
	
	pdf.savefig(fig, dpi=300)
	plt.close()
	
	fig, axs = plt.subplots(3,1, figsize=(10,14))
	
	plotting.plot_stat_map(
		thresholded_map,
		threshold=threshold_1,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title = "GLM output p < 0.005, cluster size 50 (z-scores)",
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
		title = "GLM output p < 0.005, non-parametic inference, cluster size (cluster logP)",
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
		title = "GLM output p < 0.005, non-parametic inference, cluster mass (cluster logP)",
		axes=axs[2]
	)
	
	fig.suptitle("Groupwise T-test", fontsize=16,
				 weight='bold')
	
	pdf.savefig(fig, dpi=300)
	plt.close()
	
	
