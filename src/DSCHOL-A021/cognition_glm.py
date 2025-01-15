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

fdr_threshold = 0.05


# Load fMRI images
FEOBV_img_paths = glob.glob('/OUTPUTS/DATA/*/suvr_masked_smoothed_feobv.nii.gz')

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

kbit = covariate_df_sorted['kbit'].astype(float)
mcrt_free = covariate_df_sorted['mcrt_free'].astype(float)
dsmse_total = covariate_df_sorted['dsmse_total_score'].astype(float)
dsmse_memory_composite = covariate_df_sorted['dsmse_memory_composite'].astype(float)
dsmse_non_memory_composite = covariate_df_sorted['dsmse_non_memory_composite'].astype(float)
stroop_comp = covariate_df_sorted['stroop_comp'].astype(float)
stroop_error = covariate_df_sorted['switch_acc_zscore'].astype(float)
stroop_time = covariate_df_sorted['switch_time_zscore'].astype(float)

dimx, dimy, dimz, subjects = FEOBV_imgs.shape


design_matrix_mcrt = pd.DataFrame({
	"mCRT": mcrt_free,
	"intercept": np.ones(subjects),
	"kbit": kbit
})

design_matrix_dsmse_total = pd.DataFrame({
	"dsmse_tot": dsmse_total,
	"intercept": np.ones(subjects),
	"kbit": kbit
})

design_matrix_dsmse_non_memory_composite = pd.DataFrame({
	"dsmse_non_mem": dsmse_non_memory_composite,
	"intercept": np.ones(subjects),
	"kbit": kbit
})

design_matrix_dsmse_memory_composite = pd.DataFrame({
	"dsmse_mem": dsmse_memory_composite,
	"intercept": np.ones(subjects),
	"kbit": kbit
})

design_matrix_stroop_comp = pd.DataFrame({
	"stroop_comp": stroop_comp,
	"intercept": np.ones(subjects),
	"kbit": kbit
})

design_matrix_stroop_time = pd.DataFrame({
	"stroop_time": stroop_time,
	"intercept": np.ones(subjects),
	"kbit": kbit
})

design_matrix_stroop_error = pd.DataFrame({
	"stroop_error": stroop_error,
	"intercept": np.ones(subjects),
	"kbit": kbit
})

# Load the study-specific GM mask
mask_path = 'WB_Brain_mask_prob0_3.nii'

#second level model
second_level_model_mcrt = SecondLevelModel(
	mask_img=mask_path, n_jobs=1
)
second_level_model_mcrt = second_level_model_mcrt.fit(
	FEOBV_img_paths, design_matrix=design_matrix_mcrt)
	
second_level_model_dsmse_total = SecondLevelModel(
	mask_img=mask_path, n_jobs=1
)
second_level_model_dsmse_total = second_level_model_dsmse_total.fit(
	FEOBV_img_paths, design_matrix=design_matrix_dsmse_total)

second_level_model_dsmse_non_memory_composite = SecondLevelModel(
	mask_img=mask_path, n_jobs=1
)
second_level_model_dsmse_non_memory_composite = second_level_model_dsmse_non_memory_composite.fit(
	FEOBV_img_paths, design_matrix=design_matrix_dsmse_non_memory_composite)
	
second_level_model_dsmse_memory_composite = SecondLevelModel(
	mask_img=mask_path, n_jobs=1
)
second_level_model_dsmse_memory_composite = second_level_model_dsmse_memory_composite.fit(
	FEOBV_img_paths, design_matrix=design_matrix_dsmse_memory_composite)
	
second_level_model_stroop_comp = SecondLevelModel(
	mask_img=mask_path, n_jobs=1
)
second_level_model_stroop_comp = second_level_model_stroop_comp.fit(
	FEOBV_img_paths, design_matrix=design_matrix_stroop_comp)

second_level_model_stroop_error = SecondLevelModel(
	mask_img=mask_path, n_jobs=1
)
second_level_model_stroop_error = second_level_model_stroop_error.fit(
	FEOBV_img_paths, design_matrix=design_matrix_stroop_error)

second_level_model_stroop_time = SecondLevelModel(
	mask_img=mask_path, n_jobs=1
)
second_level_model_stroop_time = second_level_model_stroop_time.fit(
	FEOBV_img_paths, design_matrix=design_matrix_stroop_time)

#calculate zmaps
z_map_mcrt = second_level_model_mcrt.compute_contrast(
	second_level_contrast=[1, 0, 0],
	output_type="z_score",
)

z_map_dsmse_total = second_level_model_dsmse_total.compute_contrast(
	second_level_contrast=[1, 0, 0],
	output_type="z_score",
)

z_map_dsmse_non_memory_composite = second_level_model_dsmse_non_memory_composite.compute_contrast(
	second_level_contrast=[1, 0, 0],
	output_type="z_score",
)

z_map_dsmse_memory_composite = second_level_model_dsmse_memory_composite.compute_contrast(
	second_level_contrast=[1, 0, 0],
	output_type="z_score",
)

z_map_stroop_comp = second_level_model_stroop_comp.compute_contrast(
	second_level_contrast=[1, 0, 0],
	output_type="z_score",
)

z_map_stroop_time = second_level_model_stroop_time.compute_contrast(
	second_level_contrast=[1, 0, 0],
	output_type="z_score",
)

z_map_stroop_error = second_level_model_stroop_error.compute_contrast(
	second_level_contrast=[1, 0, 0],
	output_type="z_score",
)


# Perform statsmap, correct for multiple comparisons
thresholded_map_mcrt, threshold_mcrt = threshold_stats_img(z_map_mcrt,
												 alpha=threshold_1,
												 cluster_threshold=50)

thresholded_map_mcrt_fdr, threshold_mcrt_fdr = threshold_stats_img(z_map_mcrt,
												 alpha=fdr_threshold,
												 height_control= 'fdr')
												 
thresholded_map_dsmse_total, threshold_dsmse_total = threshold_stats_img(z_map_dsmse_total,
												 alpha=threshold_1,
												 cluster_threshold=50)

thresholded_map_dsmse_total_fdr, threshold_dsmse_total_fdr = threshold_stats_img(z_map_dsmse_total,
															 alpha=fdr_threshold,
															 height_control='fdr')

thresholded_map_dsmse_non_memory_composite, threshold_dsmse_non_memory_composite = threshold_stats_img(z_map_dsmse_non_memory_composite,
												 alpha=threshold_1,
												 cluster_threshold=50)

thresholded_map_dsmse_non_memory_composite_fdr, threshold_dsmse_non_memory_composite_fdr = threshold_stats_img(z_map_dsmse_non_memory_composite,
												 alpha=fdr_threshold,
												 height_control= 'fdr')

thresholded_map_dsmse_memory_composite, threshold_dsmse_memory_composite = threshold_stats_img(z_map_dsmse_memory_composite,
												 alpha=threshold_1,
												 cluster_threshold=50)

thresholded_map_dsmse_memory_composite_fdr, threshold_dsmse_memory_composite_fdr = threshold_stats_img(z_map_dsmse_memory_composite,
												 alpha=fdr_threshold,
												 height_control= 'fdr')

thresholded_map_stroop_comp, threshold_stroop_comp = threshold_stats_img(z_map_stroop_comp,
												 alpha=threshold_1,
												 cluster_threshold=50)

thresholded_map_stroop_comp_fdr, threshold_stroop_comp_fdr = threshold_stats_img(z_map_stroop_comp,
												 alpha=fdr_threshold,
												 height_control= 'fdr')

thresholded_map_stroop_time, threshold_stroop_time = threshold_stats_img(z_map_stroop_time,
												 alpha=threshold_1,
												 cluster_threshold=50)

thresholded_map_stroop_time_fdr, threshold_stroop_time_fdr = threshold_stats_img(z_map_stroop_time,
												 alpha=fdr_threshold,
												 cluster_threshold='fdr')

thresholded_map_stroop_error, threshold_stroop_error = threshold_stats_img(z_map_stroop_error,
												 alpha=threshold_1,
												 cluster_threshold=50)

thresholded_map_stroop_error_fdr, threshold_stroop_error_fdr = threshold_stats_img(z_map_stroop_error,
												 alpha=fdr_threshold,
												 cluster_threshold='fdr')

# Save the statistical map
# Save the thresholded z-map to a NIfTI file
thresholded_map_mcrt.to_filename(f'{output_path}/thresholded_mcrt_effect_z_map.nii')
thresholded_map_mcrt_fdr.to_filename(f'{output_path}/thresholded_fdr_mcrt_effect_z_map.nii')

thresholded_map_dsmse_total.to_filename(f'{output_path}/thresholded_dsmse_tot_effect_z_map.nii')
thresholded_map_dsmse_total_fdr.to_filename(f'{output_path}/thresholded_fdr_dsmse_tot_effect_z_map.nii')

thresholded_map_dsmse_non_memory_composite.to_filename(f'{output_path}/thresholded_dsmse_nonmem_effect_z_map.nii')
thresholded_map_dsmse_non_memory_composite_fdr.to_filename(f'{output_path}/thresholded_fdr_dsmse_nonmem_effect_z_map.nii')

thresholded_map_dsmse_memory_composite.to_filename(f'{output_path}/thresholded_dsmse_mem_effect_z_map.nii')
thresholded_map_dsmse_memory_composite_fdr.to_filename(f'{output_path}/thresholded_fdr_dsmse_mem_effect_z_map.nii')

thresholded_map_stroop_comp.to_filename(f'{output_path}/thresholded_stroop_comp_effect_z_map.nii')
thresholded_map_stroop_comp_fdr.to_filename(f'{output_path}/thresholded_fdr_stroop_comp_effect_z_map.nii')

thresholded_map_stroop_time.to_filename(f'{output_path}/thresholded_stroop_time_effect_z_map.nii')
thresholded_map_stroop_time_fdr.to_filename(f'{output_path}/thresholded_fdr_stroop_time_effect_z_map.nii')

thresholded_map_stroop_error.to_filename(f'{output_path}/thresholded_stroop_error_effect_z_map.nii')
thresholded_map_stroop_error.to_filename(f'{output_path}/thresholded_fdr_stroop_error_effect_z_map.nii')

# Generate pdf report
pdf_filename = "/OUTPUTS/report.pdf"


with PdfPages(pdf_filename) as pdf:
	fig, axs = plt.subplots(3,1, figsize=(10,14))
	
	plotting.plot_stat_map(
		thresholded_map_mcrt,
		threshold=threshold_mcrt,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title = f"GLM mCRT output p < {threshold_1}, cluster size 50 (z-scores)",
		axes=axs[0]
	)

	plotting.plot_stat_map(
		thresholded_map_dsmse_total,
		threshold=threshold_dsmse_total,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title = f"GLM DSMSE total output p < {threshold_1}, cluster size 50 (z-scores)",
		axes=axs[1]
	)
	
	plotting.plot_stat_map(
		thresholded_map_dsmse_non_memory_composite,
		threshold=threshold_dsmse_non_memory_composite,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title = f"GLM DSMSE non-memory output p < {threshold_1}, cluster size 50 (z-scores)",
		axes=axs[2]
	)
	
	fig.suptitle("Association Between Cognition and FEOBV uptake", fontsize=16,
				 weight='bold')
	
	pdf.savefig(fig, dpi=300)
	plt.close()
	
	fig, axs = plt.subplots(3,1, figsize=(10,14))
	
	plotting.plot_stat_map(
		thresholded_map_dsmse_memory_composite,
		threshold=threshold_dsmse_memory_composite,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title = f"GLM DSMSE memory composite, p < {threshold_1}, cluster size 50 (z-scores)",
		axes=axs[0]
	)
	
	plotting.plot_stat_map(
		thresholded_map_stroop_comp,
		threshold=threshold_stroop_comp,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title = f"GLM Stroop cats & Dogs composite output p < {threshold_1}, cluster size 50 (z-scores)",
		axes=axs[1]
	)

	plotting.plot_stat_map(
		thresholded_map_stroop_error,
		threshold=threshold_stroop_error,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title = f"GLM Stroop cats & Dogs error output p < {threshold_1}, cluster size 50 (z-scores)",
		axes=axs[2]
	)
	
	pdf.savefig(fig, dpi=300)
	plt.close()

	fig, axs = plt.subplots(1, 1, figsize=(10, 14))

	plotting.plot_stat_map(
		thresholded_map_stroop_time,
		threshold=threshold_stroop_time,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title = f"GLM Stroop cats & Dogs time output p < {threshold_1}, cluster size 50 (z-scores)",
		axes=axs[2]
	)

	pdf.savefig(fig, dpi=300)
	plt.close()

	fig, axs = plt.subplots(3, 1, figsize=(10, 14))

	plotting.plot_stat_map(
		thresholded_map_mcrt_fdr,
		threshold=threshold_mcrt_fdr,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title=f"GLM mCRT output p < {fdr_threshold}, FDR corrected",
		axes=axs[0]
	)

	plotting.plot_stat_map(
		thresholded_map_dsmse_total_fdr,
		threshold=threshold_dsmse_total_fdr,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title=f"GLM DSMSE total output p < {fdr_threshold}, FDR corrected",
		axes=axs[1]
	)

	plotting.plot_stat_map(
		thresholded_map_dsmse_non_memory_composite_fdr,
		threshold=threshold_dsmse_non_memory_composite_fdr,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title=f"GLM DSMSE non-memory output p < {fdr_threshold}, FDR corrected",
		axes=axs[2]
	)

	fig.suptitle("Association Between Cognition and FEOBV uptake", fontsize=16,
				 weight='bold')

	pdf.savefig(fig, dpi=300)
	plt.close()

	fig, axs = plt.subplots(3, 1, figsize=(10, 14))

	plotting.plot_stat_map(
		thresholded_map_dsmse_memory_composite_fdr,
		threshold=threshold_dsmse_memory_composite_fdr,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title=f"GLM DSMSE memory composite, p < {fdr_threshold}, FDR corrected",
		axes=axs[0]
	)

	plotting.plot_stat_map(
		thresholded_map_stroop_comp_fdr,
		threshold=threshold_stroop_comp_fdr,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title=f"GLM Stroop cats & Dogs composite output p < {fdr_threshold}, FDR corrected",
		axes=axs[1]
	)

	plotting.plot_stat_map(
		thresholded_map_stroop_error_fdr,
		threshold=threshold_stroop_error_fdr,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title=f"GLM Stroop cats & Dogs error output p < {fdr_threshold}, FDR corrected",
		axes=axs[2]
	)

	pdf.savefig(fig, dpi=300)
	plt.close()

	fig, axs = plt.subplots(1, 1, figsize=(10, 14))

	plotting.plot_stat_map(
		thresholded_map_stroop_time_fdr,
		threshold=threshold_stroop_time_fdr,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title=f"GLM Stroop cats & Dogs time output p < {fdr_threshold}, FDR corrected",
		axes=axs[2]
	)

	pdf.savefig(fig, dpi=300)
	plt.close()






