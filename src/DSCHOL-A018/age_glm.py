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
#fdr threshold
fdr_threshold = 0.05

# Load MR images
MR_img_paths = glob.glob('/OUTPUTS/DATA/*/warped_orig.nii.gz')

MR_img_paths = sorted(MR_img_paths)

print("Data paths for age GLM set")

#generate subject list in order of import
subject_list=[]

for subject in MR_img_paths:
	path = os.path.normpath(subject)
	trcds_parts = path.split(os.sep)
	sub_id = trcds_parts[-2]
	subject_list.append(sub_id)
	
print(f'DS subject order: {subject_list}')

subs_array = np.array(subject_list)

# Load NIfTI images into a 4D image
MR_imgs = image.concat_imgs([os.path.join(data_path, img) for img in MR_img_paths])

# Import age data and sex
covariate_df = pd.read_csv('/INPUTS/covariates.csv')
covariate_df['id'] = covariate_df['id'].astype(subs_array.dtype)
covariate_df_sorted = covariate_df.set_index('id')
covariate_df_sorted = covariate_df_sorted.loc[subs_array]

age = covariate_df_sorted['dems_age'].astype(float)

sex = covariate_df_sorted['dems_sex']

#set order of sex and age to match image uploads in cluster version

sex_all, sex_all_key = pd.factorize(sex)

dimx, dimy, dimz, subjects = MR_imgs.shape

design_matrix_sex = pd.DataFrame({
	"age": age,
	"intercept": np.ones(subjects),
	"sex":sex_all
})


# Load the study-specific GM mask
mask_path = 'WB_Brain_mask_prob0_3.nii'


#second level model controlling for sex
second_level_model_sex = SecondLevelModel(
	mask_img=mask_path, n_jobs=1
)
second_level_model_sex = second_level_model_sex.fit(
	MR_img_paths, design_matrix=design_matrix_sex)


#calculate zmaps
z_map_sex = second_level_model_sex.compute_contrast(
	second_level_contrast=[1, 0, 0],
	output_type="z_score",
)


# Perform statsmap, correct for multiple comparisons
thresholded_map_sex, threshold_sex = threshold_stats_img(z_map_sex,
												 alpha=threshold_1,
												 cluster_threshold=50)

thresholded_map_sex_fdr, threshold_sex_fdr = threshold_stats_img(z_map_sex,
												 alpha=fdr_threshold, height_control="fdr"
												 )


# Save the statistical map
# Save the thresholded z-map to a NIfTI file
thresholded_map_sex.to_filename(f'{output_path}/thresholded_age_effect_sex_controlled_z_map.nii')
thresholded_map_sex_fdr.to_filename(f'{output_path}/fdr_thresholded_age_effect_sex_controlled_z_map.nii')

# Generate pdf report
pdf_filename = "/OUTPUTS/report.pdf"

with PdfPages(pdf_filename) as pdf:
	fig, axs = plt.subplots(2,1, figsize=(10,14))
	
	plotting.plot_stat_map(
		thresholded_map_sex,
		threshold=threshold_sex,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title = f"GLM output p < {threshold_1}, cluster size 50 (z-scores)",
		axes=axs[0]
	)
	
	plotting.plot_stat_map(
		thresholded_map_sex_fdr,
		threshold=threshold_sex_fdr,
		colorbar=True,
		cut_coords=6,
		display_mode="x",
		figure=fig,
		title = f"GLM output fdr-corrected p < {fdr_threshold} (threshold: {threshold_sex_fdr})",
		axes=axs[1]
	)
	
	pdf.savefig(fig, dpi=300)
	plt.close()




