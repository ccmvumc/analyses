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
from nilearn.image import math_img
from config import out_dir, in_dir

atlas_ni = datasets.load_mni152_template()

# Import atlas file generated in normalize.py
atlas=f'{out_dir}/atlasni.nii.gz'
fixed = ants.image_read(atlas)

for subject in sorted(os.listdir(in_dir)):
	if subject.startswith('.'):
		# ignore hidden files and other junk
		continue
	
	if subject.startswith('covariates'):
		# ignore covariates csv
		continue
	
	
	subject_out = f'{out_dir}/{subject}'
	
	#resample MRI to same as PET images for mask generation
	#import preprocessed PET
	pet = image.load_img(f'{out_dir}/{subject}/smoothed_warped_FEOBV.nii.gz')
	mr = image.load_img(f'{out_dir}/{subject}/warped_orig.nii.gz')
	resampled_mr = image.resample_to_img(mr, pet)
	
	#import cerebellar segmentation
	cblm = image.load_img(f'{out_dir}/{subject}/cerebellum_mask_deep_atropos.nii.gz')
	
	#invert
	inverted_cblm = math_img('1 - img', img=cblm)
	
	#apply nilearn mask
	gm_mask = masking.compute_brain_mask(resampled_mr, mask_type='gm')
	
	#combine masks
	
	individual_mask = math_img('img1 * img2', img1=gm_mask, img2=inverted_cblm)
	
	#output nilearn mask for specific subject for input into study specific mask
	#script
	
	individual_mask.to_filename(f'{subject_out}/gmmask.nii.gz')
	
print("Individualized masks generated")
	
	


