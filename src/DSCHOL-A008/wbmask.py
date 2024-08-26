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

mask_nii = new_img_like(
    'DST3050001/smoothed_warped_FEOBV.nii.gz', dilerodilero_mask.astype(int)
)

nib.save(mask_nii, "WB_Brain_mask_prob0_3.nii")
            


            
