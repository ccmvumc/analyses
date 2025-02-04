#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 10:13:11 2024

@author: jason
"""

import os

import ants
from nilearn import datasets
from nilearn import image
from nilearn.image import math_img
from config import in_dir, out_dir

atlas_ni = datasets.load_mni152_template()

atlas_path = '/Users/jasonrussell/Documents/code/analyses_local/atlases'
atlas_ds=f'{atlas_path}/CS_DS_Intensity.nii.gz'

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

	if subject.startswith('atlas'):
		# ignore covariates csv
		continue
	
	
	subject_out = f'{out_dir}/{subject}'

	#import cerebellar segmentation
	cblm = image.load_img(f'{out_dir}/{subject}/cerebellum_mask_deep_atropos.nii.gz')

	#invert
	inverted_cblm = math_img('1 - img', img=cblm)
	
	#import subject gm mask
	gm_mask_ds = image.load_img(f'{out_dir}/{subject}/gm_ds.nii.gz')

	# combine masks

	individual_mask = math_img('img1 * img2', img1=gm_mask_ds, img2=inverted_cblm)
	
	#output nilearn mask for specific subject for input into study specific mask
	#script
	
	individual_mask.to_filename(f'{subject_out}/wbmask.nii.gz')
	
print("Individualized masks generated")



