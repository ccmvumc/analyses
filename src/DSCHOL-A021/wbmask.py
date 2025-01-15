#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spyder Editor
Author: Jason Russell.
Script to Generate Study Specific Mask from Individual T1s
"""

from nilearn import image
from nilearn.image import new_img_like
import nibabel as nib
import os
import numpy as np
from scipy.ndimage import binary_dilation
from scipy.ndimage import binary_erosion
import glob

#Set path where data is stored
data_path = '/OUTPUTS/DATA'

#path to individual subject masks
FEOBV_files = glob.glob('/OUTPUTS/DATA/*/wbmask.nii.gz')

os.chdir(data_path)

#Import individual nifti masks in a 4D array
ind_masks = image.get_data(FEOBV_files)

#Generate single array for value with probability voxel is GM per participant
#get shapes of 4D arrays
rsdim1, rsdim2, rsdim3, subjects = ind_masks.shape

# Initialize array to store probabilities
prob_mask = np.zeros((rsdim1, rsdim2, rsdim3))

#Itterate through array calculating probability of voxel being GM
# Perform linear regression for each cell
for i in range(rsdim1):
    for j in range(rsdim2):
        for k in range(rsdim3):
            if (np.sum(ind_masks[i, j, k, :]))/subjects >= 0.3:
                prob_mask[i, j, k] = 1
            else:
                prob_mask[i, j, k] = 0
                

dil_mask = binary_dilation(prob_mask)
dilero_mask = binary_erosion(dil_mask)
dilerodil_mask = binary_dilation(dilero_mask)
dilerodilero_mask = binary_erosion(dilerodil_mask)

# import averaged FEOBV mask
feobv_suvr_mask = f'{data_path}/averaged_feobv_mask.nii.gz'
feobv_suvr_mask_img = nib.load(feobv_suvr_mask)

# convert image to binary image
feobv_suvr_mask_data = feobv_suvr_mask_img.get_fdata()

# add to average mask
combined_mask_data = (dilerodilero_mask > 0) & (feobv_suvr_mask_data > 0)

mask_gm_nii = new_img_like(
    feobv_suvr_mask, combined_mask_data.astype(int)
)

nib.save(mask_gm_nii, "Brain_mask_prob0_3.nii")
            


            
