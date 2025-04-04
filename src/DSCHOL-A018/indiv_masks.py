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
	
	if subject.startswith('covariates'):
		# ignore covariates csv
		continue
	
	
	subject_out = f'{out_dir}/{subject}'
	
	#load mr in MNI-space
	mr = image.load_img(f'/OUTPUTS/DATA/{subject}/warped_orig.nii.gz')
	
	
	#apply nilearn mask
	wb_mask = masking.compute_brain_mask(mr, mask_type='whole-brain')
	
	#apply wm mask
	wm_mask = masking.compute_brain_mask(mr, mask_type='wm')
	
	#invert wm_mask
	
	inverted_wm_mask = math_img('1 - img', img=wm_mask)
	
	whole_brain_without_wm = math_img('img1 * img2', img1=wb_mask, img2=inverted_wm_mask)
	
	#output nilearn mask for specific subject for input into study specific mask
	#script
	
	whole_brain_without_wm.to_filename(f'{subject_out}/wbmask.nii.gz')
	
print("Individualized masks generated")



