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
threshold_non_para = 0.005
#significance of clusters following non-parametric inference
cluster_thres = -np.log10(0.05)

#set number of permutations for non-parametric inference (10000 when finalized
# but adds compute time, 500 for running on computer)
permutations = 10000

# Load fMRI images
FEOBV_img_paths = glob.glob('/OUTPUTS/DATA/*/smoothed_warped_FEOBV.nii.gz')

FEOBV_img_paths = sorted(FEOBV_img_paths)

print("Data paths for age GLM set")

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

age = covariate_df_sorted['dems_age'].astype(float)

sex = covariate_df_sorted['dems_sex']

#set order of sex and age to match image uploads in cluster version

sex_all, sex_all_key = pd.factorize(sex)

dimx, dimy, dimz, subjects = FEOBV_imgs.shape


design_matrix = pd.DataFrame({
	"age": age,
	"intercept": np.ones(subjects)
})

design_matrix_sex = pd.DataFrame({
	"age": age,
	"intercept": np.ones(subjects),
	"sex":sex_all
})


# Load the study-specific GM mask
mask_path = 'WB_Brain_mask_prob0_3.nii'

#second level model
second_level_model = SecondLevelModel(
	mask_img=mask_path, n_jobs=1
)
second_level_model = second_level_model.fit(
	FEOBV_img_paths, design_matrix=design_matrix)

#second level model controlling for sex
second_level_model_sex = SecondLevelModel(
	mask_img=mask_path, n_jobs=1
)
second_level_model_sex = second_level_model.fit(
	FEOBV_img_paths, design_matrix=design_matrix_sex)


#calculate zmaps
z_map = second_level_model.compute_contrast(
	second_level_contrast=[1, 0],
	output_type="z_score",
)

z_map_sex = second_level_model_sex.compute_contrast(
	second_level_contrast=[1, 0, 0],
	output_type="z_score",
)


# Perform statsmap, correct for multiple comparisons
thresholded_map, threshold = threshold_stats_img(z_map,
												 alpha=threshold_1,
												 cluster_threshold=50)

thresholded_map_sex, threshold_sex = threshold_stats_img(z_map_sex,
												 alpha=threshold_1,
												 cluster_threshold=50)


# Save the statistical map
# Save the thresholded z-map to a NIfTI file
thresholded_map.to_filename(f'{output_path}/thresholded_age_effect_z_map.nii')
thresholded_map_sex.to_filename(f'{output_path}/thresholded_age_effect_sex_controlled_z_map.nii')

#perform non parametric inference
corrected_map = non_parametric_inference(
	FEOBV_img_paths,
	design_matrix=design_matrix,
	second_level_contrast=[1,0],
	mask=mask_path,
	n_perm=permutations,
	two_sided_test=True,
	n_jobs=1,
	threshold=threshold_non_para
	)

#perform non parametric inference
corrected_map_sex = non_parametric_inference(
	FEOBV_img_paths,
	design_matrix=design_matrix_sex,
	second_level_contrast=[1,0,0],
	mask=mask_path,
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

# extract cluster significance <0.05
img_data_non_para_sex = corrected_map_sex['logp_max_size'].get_fdata()
img_data_non_para_sex[img_data_non_para_sex < cluster_thres] = 0
img_data_non_para_mask_sex = img_data_non_para_sex != 0
thresholded_map_np_sex = np.where(img_data_non_para_mask_sex, img_data_non_para_sex, np.nan)

thresholded_map_np_ni = new_img_like('DST3050001/smoothed_warped_FEOBV.nii.gz', thresholded_map_np)

thresholded_map_np_ni_sex = new_img_like('DST3050001/smoothed_warped_FEOBV.nii.gz', thresholded_map_np_sex)

# Save non-parametric inference corrected map
thresholded_map_np_ni.to_filename(f'{output_path}/Age_glm_non_parametric_inference_corrected_logP_map.nii')

thresholded_map_np_ni_sex.to_filename(f'{output_path}/Age_glm_sex_correct_non_parametric_inference_corrected_logP_map.nii')

# Generate pdf report
pdf_filename = "/OUTPUTS/report.pdf"


with PdfPages(pdf_filename) as pdf:
	fig, axs = plt.subplots(3,1, figsize=(10,14))
	
	plotting.plot_stat_map(
		thresholded_map,
		threshold=threshold,
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
		title = f"GLM output p < {threshold_non_para}, non-parametic inference, cluster size {cluster_thres} (cluster logP)",
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
		title = f"GLM output p < {threshold_non_para}, non-parametic inference, cluster mass, {cluster_thres} (cluster logP)",
		axes=axs[2]
	)
	
	fig.suptitle("Association Between Age and FEOBV uptake", fontsize=16,
				 weight='bold')
	
	pdf.savefig(fig, dpi=300)
	plt.close()
	
	fig, axs = plt.subplots(3,1, figsize=(10,14))
	
	plotting.plot_stat_map(
		thresholded_map_sex,
		threshold=threshold_sex,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title = f"GLM output, sex controlled, p < {threshold_1}, cluster size 50 (z-scores)",
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
		title = f"GLM output, sex controlled, p < {threshold_non_para}, non-parametic inference, cluster size, {cluster_thres} (cluster logP)",
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
		title = f"GLM output, sex controlled, p < {threshold_non_para}, non-parametic inference, cluster mass, p < {cluster_thres} (cluster logP)",
		axes=axs[2]
	)
	
	fig.suptitle("Association Between Age and FEOBV uptake", fontsize=16,
				 weight='bold')
	
	pdf.savefig(fig, dpi=300)
	plt.close()




