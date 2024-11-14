# -*- coding: utf-8 -*-
"""
Spyder Editor
Author: Jason Russell.
Script to perform Voxel-wise linear regression between FEOBV and age
"""

from nilearn import image
from nilearn.glm.second_level import SecondLevelModel
from nilearn.glm import threshold_stats_img
import pandas as pd
import os
import numpy as np
from nilearn import plotting
import matplotlib.pyplot as plt
from nilearn.glm.second_level import non_parametric_inference
from nilearn.image import new_img_like
from matplotlib.backends.backend_pdf import PdfPages
import glob

#Set path where data is stored
data_path = '/OUTPUTS/DATA'


os.chdir(data_path)
output_path = '/OUTPUTS/DATA'

#set signficant thresholds for different tests
#significance (p-val) for initial test at cluster threshold 50
threshold_1 = 0.005


# Load fMRI images
FEOBV_img_paths = glob.glob('/OUTPUTS/DATA/*/smoothed_warped_FEOBV.nii.gz')

FEOBV_img_paths = sorted(FEOBV_img_paths)

print("Data paths for cognition GLM set")

#generate subject list in order of import
subject_list=[]

for subject in FEOBV_img_paths:
	path = os.path.normpath(subject)
	trcds_parts = path.split(os.sep)
	sub_id = trcds_parts[-2]
	subject_list.append(sub_id)
	
print(f'DS subject order: {subject_list}')

subs_array = np.array(subject_list)

# Load NIfTI images into a 4D image
FEOBV_imgs = image.concat_imgs([os.path.join(data_path, img) for img in FEOBV_img_paths])

# Import age data and sex
covariate_df = pd.read_csv('/INPUTS/covariates.csv')
covariate_df['id'] = covariate_df['id'].astype(subs_array.dtype)
covariate_df_sorted = covariate_df.set_index('id')
covariate_df_sorted = covariate_df_sorted.loc[subs_array]

RBANS = covariate_df_sorted['RBANS'].astype(float)
RBANS_visuospatial = covariate_df_sorted['RBANS_visuospatial'].astype(float)
RBANS_immediate_memory = covariate_df_sorted['RBANS_immediate_memory'].astype(float)
RBANS_language = covariate_df_sorted['RBANS_language'].astype(float)
RBANS_attention = covariate_df_sorted['RBANS_attention'].astype(float)
RBANS_delayedmem = covariate_df_sorted['RBANS_delayedmem'].astype(float)

dimx, dimy, dimz, subjects = FEOBV_imgs.shape


design_matrix_RBANS_visuospatial = pd.DataFrame({
	"RBANS_visuospatial": RBANS_visuospatial,
	"intercept": np.ones(subjects),
})

design_matrix_RBANS_immediate_memory = pd.DataFrame({
	"RBANS_immediate_memory": RBANS_immediate_memory,
	"intercept": np.ones(subjects),
})

design_matrix_RBANS_attention = pd.DataFrame({
	"RBANS_attention": RBANS_attention,
	"intercept": np.ones(subjects),
})

design_matrix_RBANS_language = pd.DataFrame({
	"RBANS_language": RBANS_language,
	"intercept": np.ones(subjects),
})

design_matrix_RBANS_delayedmem = pd.DataFrame({
	"RBANS_delayedmem": RBANS_delayedmem,
	"intercept": np.ones(subjects),
})

design_matrix_RBANS = pd.DataFrame({
	"RBANS": RBANS,
	"intercept": np.ones(subjects),
})

# Load the study-specific GM mask
mask_path = 'WB_Brain_mask_prob0_3.nii'

#second level model
second_level_model_RBANS_visuospatial = SecondLevelModel(
	mask_img=mask_path, n_jobs=1
)
second_level_model_RBANS_visuospatial = second_level_model_RBANS_visuospatial.fit(
	FEOBV_img_paths, design_matrix=design_matrix_RBANS_visuospatial)
	
second_level_model_RBANS_immediate_memory = SecondLevelModel(
	mask_img=mask_path, n_jobs=1
)
second_level_model_RBANS_immediate_memory = second_level_model_RBANS_immediate_memory.fit(
	FEOBV_img_paths, design_matrix=design_matrix_RBANS_immediate_memory)

second_level_model_RBANS_attention = SecondLevelModel(
	mask_img=mask_path, n_jobs=1
)
second_level_model_RBANS_attention = second_level_model_RBANS_attention.fit(
	FEOBV_img_paths, design_matrix=design_matrix_RBANS_attention)
	
second_level_model_RBANS_language = SecondLevelModel(
	mask_img=mask_path, n_jobs=1
)
second_level_model_RBANS_language = second_level_model_RBANS_language.fit(
	FEOBV_img_paths, design_matrix=design_matrix_RBANS_language)
	
second_level_model_RBANS_delayedmem = SecondLevelModel(
	mask_img=mask_path, n_jobs=1
)
second_level_model_RBANS_delayedmem = second_level_model_RBANS_delayedmem.fit(
	FEOBV_img_paths, design_matrix=design_matrix_RBANS_delayedmem)

second_level_model_RBANS = SecondLevelModel(
	mask_img=mask_path, n_jobs=1
)
second_level_model_RBANS = second_level_model_RBANS.fit(
	FEOBV_img_paths, design_matrix=design_matrix_RBANS)

#calculate zmaps
z_map_RBANS_visuospatial = second_level_model_RBANS_visuospatial.compute_contrast(
	second_level_contrast=[1, 0],
	output_type="z_score",
)

z_map_RBANS_immediate_memory = second_level_model_RBANS_immediate_memory.compute_contrast(
	second_level_contrast=[1, 0],
	output_type="z_score",
)

z_map_RBANS_attention = second_level_model_RBANS_attention.compute_contrast(
	second_level_contrast=[1, 0],
	output_type="z_score",
)

z_map_RBANS_language = second_level_model_RBANS_language.compute_contrast(
	second_level_contrast=[1, 0],
	output_type="z_score",
)

z_map_RBANS_delayedmem = second_level_model_RBANS_delayedmem.compute_contrast(
	second_level_contrast=[1, 0],
	output_type="z_score",
)

z_map_RBANS = second_level_model_RBANS.compute_contrast(
	second_level_contrast=[1, 0],
	output_type="z_score",
)


# Perform statsmap, correct for multiple comparisons
thresholded_map_RBANS_visuospatial, threshold_RBANS_visuospatial = threshold_stats_img(z_map_RBANS_visuospatial,
																					   alpha=threshold_1,
																					   cluster_threshold=50)
												 
thresholded_map_RBANS_immediate_memory, threshold_RBANS_immediate_memory = threshold_stats_img(z_map_RBANS_immediate_memory,
																							   alpha=threshold_1,
																							   cluster_threshold=50)

thresholded_map_RBANS_attention, threshold_RBANS_attention = threshold_stats_img(z_map_RBANS_attention,
																				 alpha=threshold_1,
																				 cluster_threshold=50)

thresholded_map_RBANS_language, threshold_RBANS_language = threshold_stats_img(z_map_RBANS_language,
																			   alpha=threshold_1,
																			   cluster_threshold=50)

thresholded_map_RBANS_delayedmem, threshold_RBANS_delayedmem = threshold_stats_img(z_map_RBANS_delayedmem,
																				   alpha=threshold_1,
																				   cluster_threshold=50)

thresholded_map_RBANS, threshold_RBANS = threshold_stats_img(z_map_RBANS,
															   alpha=threshold_1,
															   cluster_threshold=50)

# Save the statistical map
# Save the thresholded z-map to a NIfTI file
thresholded_map_RBANS_visuospatial.to_filename(f'{output_path}/thresholded_RBANS_visuospatialt_effect_z_map.nii')

thresholded_map_RBANS_immediate_memory.to_filename(f'{output_path}/thresholded_RBANS_immediate_memory_effect_z_map.nii')

thresholded_map_RBANS_attention.to_filename(f'{output_path}/thresholded_dRBANS_attention_effect_z_map.nii')

thresholded_map_RBANS_language.to_filename(f'{output_path}/thresholded_RBANS_language_effect_z_map.nii')

thresholded_map_RBANS_delayedmem.to_filename(f'{output_path}/thresholded_RBANS_delayedmem_effect_z_map.nii')

thresholded_map_RBANS.to_filename(f'{output_path}/thresholded_RBANS_effect_z_map.nii')


# Generate pdf report
pdf_filename = "/OUTPUTS/report.pdf"


with PdfPages(pdf_filename) as pdf:
	fig, axs = plt.subplots(3,1, figsize=(10,14))
	
	plotting.plot_stat_map(
		thresholded_map_RBANS_visuospatial,
		threshold=threshold_RBANS_visuospatial,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title = f"GLM RBANS_visuospatial output p < {threshold_1}, cluster size 50 (z-scores)",
		axes=axs[0]
	)

	plotting.plot_stat_map(
		thresholded_map_RBANS_immediate_memory,
		threshold=threshold_RBANS_immediate_memory,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title = f"GLM RBANS_immediate_memory total output p < {threshold_1}, cluster size 50 (z-scores)",
		axes=axs[1]
	)
	
	plotting.plot_stat_map(
		thresholded_map_RBANS_attention,
		threshold=threshold_RBANS_attention,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title = f"GLM RBANS_attention output p < {threshold_1}, cluster size 50 (z-scores)",
		axes=axs[2]
	)
	
	fig.suptitle("Association Between Cognition and FEOBV uptake", fontsize=16,
				 weight='bold')
	
	pdf.savefig(fig, dpi=300)
	plt.close()
	
	fig, axs = plt.subplots(3,1, figsize=(10,14))
	
	plotting.plot_stat_map(
		thresholded_map_RBANS_language,
		threshold=threshold_RBANS_language,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title = f"GLM RBANS_language, p < {threshold_1}, cluster size 50 (z-scores)",
		axes=axs[0]
	)
	
	plotting.plot_stat_map(
		thresholded_map_RBANS_delayedmem,
		threshold=threshold_RBANS_delayedmem,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title = f"GLM RBANS_delayedmem output p < {threshold_1}, cluster size 50 (z-scores)",
		axes=axs[1]
	)

	plotting.plot_stat_map(
		thresholded_map_RBANS,
		threshold=threshold_RBANS,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title = f"GLM RBANS output p < {threshold_1}, cluster size 50 (z-scores)",
		axes=axs[2]
	)
	
	pdf.savefig(fig, dpi=300)
	plt.close()




