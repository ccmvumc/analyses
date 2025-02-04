#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""
Spyder Editor
Author: Jason Russell.
Script to perform Voxel-wise linear regression between FEOBV and centiloid
"""

import glob
from nilearn import image
from nilearn.glm.second_level import SecondLevelModel
from nilearn.glm.second_level import non_parametric_inference
from nilearn.glm import threshold_stats_img, fdr_threshold
import pandas as pd
import os
import numpy as np
from nilearn import plotting
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from nilearn.image import new_img_like
from config import out_dir, covariates

os.chdir(out_dir)



#set signficant thresholds for different tests
#significance (p-val) for initial test at cluster threshold 50
threshold_1 = 0.005
threshold_non_para = 0.005
#significance of clusters following non-parametric inference
cluster_thres = -np.log10(0.05)

fdrthres = 0.05


#set number of permutations for non-parametric inference (10000 when finalized
# but adds compute time, 500 for running on computer)
permutations = 10000

# Load PET images
FEOBV_img_paths = glob.glob(f'{out_dir}/*/smoothed_warped_FEOBV.nii.gz')

FEOBV_img_paths = sorted(FEOBV_img_paths)

subject_list=[]

for subject in FEOBV_img_paths:
	path = os.path.normpath(subject)
	FEOBV_parts = path.split(os.sep)
	sub_id = FEOBV_parts[-2]
	subject_list.append(sub_id)
	
print(f'DS subject order: {subject_list}')

subs_array = np.array(subject_list)

# Load NIfTI images into a 4D image
FEOBV_imgs = image.concat_imgs([os.path.join(out_dir, img) for img in FEOBV_img_paths])

# Import centiloid data and sort
centiloid_df = pd.read_csv(f'{covariates}/covariates.csv')
centiloid_df['id'] = centiloid_df['id'].astype(subs_array.dtype)
centiloid_df_sorted = centiloid_df.set_index('id')
centiloid_df_sorted = centiloid_df_sorted.loc[subs_array]

centiloid = centiloid_df_sorted['Centiloid'].astype(float)
age = centiloid_df_sorted['dems_age'].astype(float)

sex_all, sex_all_key = pd.factorize(centiloid_df_sorted['dems_sex'])

print('Covariates loaded and sorted')
print(centiloid_df_sorted)

dimx, dimy, dimz, subjects = FEOBV_imgs.shape


design_matrix = pd.DataFrame({
	"centiloid": centiloid,
	"intercept": np.ones(subjects)
})

design_matrix_age = pd.DataFrame({
	"centiloid": centiloid,
	"intercept": np.ones(subjects),
	"age": age
})

design_matrix_sex = pd.DataFrame({
	"centiloid": centiloid,
	"intercept": np.ones(subjects),
	"sex": sex_all
})

design_matrix_sexage = pd.DataFrame({
	"centiloid": centiloid,
	"intercept": np.ones(subjects),
	"sex": sex_all,
	"age": age
})


# Load the study-specific GM mask
gmmask_path = f'{out_dir}/study_specific_GM_mask_prob0_3.nii'

#second level model
second_level_model = SecondLevelModel(
	mask_img=gmmask_path, n_jobs=1
)
second_level_model = second_level_model.fit(
	FEOBV_img_paths, design_matrix=design_matrix)

#second level model_sex
second_level_model_sex = SecondLevelModel(
	mask_img=gmmask_path, n_jobs=1
)
second_level_model_sex = second_level_model_sex.fit(
	FEOBV_img_paths, design_matrix=design_matrix_sex)

#second level model_age
second_level_model_age = SecondLevelModel(
	mask_img=gmmask_path, n_jobs=1
)
second_level_model_age = second_level_model_age.fit(
	FEOBV_img_paths, design_matrix=design_matrix_age)
	
#second level model_sexage
second_level_model_sexage = SecondLevelModel(
	mask_img=gmmask_path, n_jobs=1
)
second_level_model_sexage = second_level_model_sexage.fit(
	FEOBV_img_paths, design_matrix=design_matrix_sexage)

#calculate zmaps
z_map = second_level_model.compute_contrast(
	second_level_contrast=[1, 0],
	output_type="z_score",
)

z_map_sex = second_level_model_sex.compute_contrast(
	second_level_contrast=[1, 0, 0],
	output_type="z_score",
)

z_map_age = second_level_model_age.compute_contrast(
	second_level_contrast=[1, 0, 0],
	output_type="z_score",
)

z_map_sexage = second_level_model_sexage.compute_contrast(
	second_level_contrast=[1, 0, 0, 0],
	output_type="z_score",
)



# Perform statsmap, correct for multiple comparisons
thresholded_map, threshold = threshold_stats_img(z_map,
												 alpha=threshold_1,
												 cluster_threshold=50)
												 
thresholded_map_sex, threshold_sex = threshold_stats_img(z_map_sex,
												 alpha=threshold_1,
												 cluster_threshold=50)
											
thresholded_map_age, threshold_age = threshold_stats_img(z_map_age,
												 alpha=threshold_1,
												 cluster_threshold=50)
												 
thresholded_map_sexage, threshold_sexage = threshold_stats_img(z_map_sexage,
												 alpha=threshold_1,
												 cluster_threshold=50)

#fdr correct
thresholded_map_fdr, threshold_fdr = threshold_stats_img(z_map,
												 alpha=fdrthres,
												 height_control= 'fdr')

thresholded_map_age_fdr, threshold_age_fdr = threshold_stats_img(z_map_age,
												 alpha=fdrthres,
												 height_control='fdr')

# Save the statistical map
# Save the thresholded z-map to a NIfTI file
thresholded_map.to_filename(f'{out_dir}/Centiloid_glm_zmap.nii')
thresholded_map_sex.to_filename(f'{out_dir}/Centiloid_glm_zmap_sex.nii')
thresholded_map_age.to_filename(f'{out_dir}/Centiloid_glm_zmap_age.nii')
thresholded_map_sexage.to_filename(f'{out_dir}/Centiloid_glm_zmap_sex+age.nii')

thresholded_map_fdr.to_filename(f'{out_dir}/Centiloid_fdr_glm_zmap.nii')
thresholded_map_age_fdr.to_filename(f'{out_dir}/Centiloid_fdr_glm_zmap_age.nii')

#perform non parametric inference
#corrected_map = non_parametric_inference(
#	FEOBV_img_paths,
#	design_matrix=design_matrix,
#	second_level_contrast=[1,0],
#	mask=gmmask_path,
#	n_perm=permutations,
#	two_sided_test=True,
#	n_jobs=1,
#	threshold=threshold_non_para
#	)

# extract cluster significance <0.05
#img_data_non_para = corrected_map['logp_max_size'].get_fdata()
#img_data_non_para[img_data_non_para < cluster_thres] = 0
#img_data_non_para_mask = img_data_non_para != 0
#thresholded_map_np = np.where(img_data_non_para_mask, img_data_non_para, np.nan)

#thresholded_map_np_ni = new_img_like('DST3050001/smoothed_warped_FEOBV.nii.gz', thresholded_map_np)

# Save non-parametric inference corrected map
#thresholded_map_np_ni.to_filename(f'{out_dir}/Centiloid_glm_non_parametric_inference_corrected_logP_map.nii')

# Generate pdf report
pdf_filename = "OUTPUTS/report.pdf"

with PdfPages(pdf_filename) as pdf:
    # First set of plots
    fig1, axs1 = plt.subplots(3, 1, figsize=(10, 14))

    plotting.plot_stat_map(
        thresholded_map,
        threshold=threshold,
        colorbar=True,
        cut_coords=6,
        display_mode="x",
        figure=fig1,
        title="GLM output p < 0.005, cluster size 50 (z-scores)",
        axes=axs1[0]
    )

    plotting.plot_stat_map(
        thresholded_map_fdr,
        threshold=fdrthres,
        colorbar=True,
        cut_coords=6,
        display_mode="x",
        figure=fig1,
        title="GLM output p < 0.05, FDR corrected",
        axes=axs1[1]
    )

    plotting.plot_stat_map(
        thresholded_map_age_fdr,
        threshold=fdrthres,
        colorbar=True,
        cut_coords=6,
        display_mode="x",
        figure=fig1,
        title="GLM output, age as covariate p < 0.05, FDR corrected",
        axes=axs1[2]
    )

    fig1.suptitle(
        "Association Between Centiloid Value and FEOBV uptake",
        fontsize=16, weight="bold"
    )
    pdf.savefig(fig1, dpi=300)
    plt.close(fig1)

    # Second set of plots
    fig2, axs2 = plt.subplots(3, 1, figsize=(10, 14))

    plotting.plot_stat_map(
        thresholded_map_sex,
        threshold=threshold_sex,
        colorbar=True,
        cut_coords=6,
        display_mode="x",
        figure=fig2,
        title="GLM output, sex controlled p < 0.005, cluster size 50 (z-scores)",
        axes=axs2[0]
    )

    plotting.plot_stat_map(
        thresholded_map_age,
        threshold=threshold_age,
        colorbar=True,
        cut_coords=6,
        display_mode="x",
        figure=fig2,
        title="GLM output, age controlled p < 0.005, cluster size 50 (z-scores)",
        axes=axs2[1]
    )

    plotting.plot_stat_map(
        thresholded_map_sexage,
        threshold=threshold_sexage,
        colorbar=True,
        cut_coords=6,
        display_mode="x",
        figure=fig2,
        title="GLM output, sex and age controlled p < 0.005, cluster size 50 (z-scores)",
        axes=axs2[2]
    )

    fig2.suptitle(
        "Association Between Centiloid Value and FEOBV uptake",
        fontsize=16, weight="bold"
    )
    pdf.savefig(fig2, dpi=300)
    plt.close(fig2)




