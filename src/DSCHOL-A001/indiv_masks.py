#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 10:13:11 2024

@author: jason
"""

import os

import ants
from nilearn import datasets
from nilearn import masking
from nilearn import image

in_dir = '/INPUTS'
atlas_ni = datasets.load_mni152_template()
out_dir = '/OUTPUTS/DATA'

# Import atlas file generated in normalize.py
atlas=f'{out_dir}/atlasni.nii.gz'
fixed = ants.image_read(atlas)

for subject in sorted(os.listdir(in_dir)):
	if subject.startswith('.'):
		# ignore hidden files and other junk
		continue
	
	if subject.startswith('covariate'):
		# ignore covariates.csv
		continue
	
	subject_out = f'{out_dir}/{subject}'
	
	#resample MRI to same as PET images for mask generation
	#import preprocessed PET
	pet = image.load_img(f'/OUTPUTS/DATA/{subject}/smoothed_warped_FEOBV.nii.gz')
	mr = image.load_img(f'/OUTPUTS/DATA/{subject}/warped_orig.nii.gz')
	resampled_mr = image.resample_to_img(mr, pet)
	
	
	#apply nilearn mask
	individual_mask = masking.compute_brain_mask(resampled_mr, mask_type='gm')
	
	#output nilearn mask for specific subject for input into study specific mask
	#script
	
	individual_mask.to_filename(f'{subject_out}/gmmask.nii.gz')
	
print("Individualized masks generated")
	
	


