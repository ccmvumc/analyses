import glob
import os

import ants
from antspynet import brain_extraction
from nilearn import datasets
import nibabel as nib


in_dir = '/INPUTS'
atlas_ni = datasets.load_mni152_template()
out_dir = '/OUTPUTS/DATA'


# Convert atlas_file to ants image fixed target for registration
os.makedirs(out_dir)
nib.save(atlas_ni, f'{out_dir}/atlasni.nii.gz')
atlas=f'{out_dir}/atlasni.nii.gz'
fixed = ants.image_read(atlas)

for subject in sorted(os.listdir(in_dir)):
	if subject.startswith('.'):
		# ignore hidden files and other junk
		continue
	if subject.startswith('covariates'):
		# ignore covariates csv
		continue

	subject_feobv = glob.glob(f'{in_dir}/{subject}/assessors/*FEOBVQA_USC_NOPVC_v4*')[0]

	print('MRI:', subject_feobv)

	subject_out = f'{out_dir}/{subject}'

	os.makedirs(subject_out)

	# Get full file path to input images
	orig_file = f'{subject_feobv}/mri/orig.mgz'
	
	# Skull Strip Original T1
	raw = ants.image_read(orig_file)
	extracted_mask = brain_extraction(raw, modality='t1')

	#Apply mask with skull stripped
	masked_image = ants.mask_image(raw, extracted_mask)

	# Load orig T1 image as moving image for registration
	moving = masked_image

	# Do Registration of Moving to Fixed
	reg = ants.registration(fixed, moving, type_of_transform='SyN')

	# Save warped orig
	warped_orig_file = f'{subject_out}/warped_orig.nii.gz'
	ants.image_write(reg['warpedmovout'], warped_orig_file)
