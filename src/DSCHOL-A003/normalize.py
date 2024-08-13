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

	subject_feobv = glob.glob(f'{in_dir}/{subject}/assessors/*FEOBVQA_v4*')[0]
	subject_pib = glob.glob(f'{in_dir}/{subject}/assessors/*PIBQA_v3*')[0]

	print('FEOBV:', subject_feobv)
	print('PIB:', subject_pib)

	subject_out = f'{out_dir}/{subject}'

	os.makedirs(subject_out)

	# Get full file path to input images
	orig_file = f'{subject_feobv}/mri/orig.mgz'
	feobv_file =  f'{subject_feobv}/gtmpvc.esupravwm.output/rbv.nii.gz'
	pib_file =  f'{subject_pib}/gtmpvc.cblmgmwm.output/rbv.nii.gz'
	
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

	# Apply transform to PIB image which is already in same space
	warped_pib_file = f'{subject_out}/warped_PIB.nii.gz'
	pib = ants.image_read(pib_file)
	warped_pib = ants.apply_transforms(fixed, pib, reg['fwdtransforms'])
	ants.image_write(warped_pib, warped_pib_file)

	# Apply transform to FEOBV image which is already in same space
	warped_feobv_file = f'{subject_out}/warped_FEOBV.nii.gz'
	feobv = ants.image_read(feobv_file)
	warped_feobv = ants.apply_transforms(fixed, feobv, reg['fwdtransforms'])
	ants.image_write(warped_feobv, warped_feobv_file)

	# Smoothing PIB
	smoothed_warped_pib_file = f'{subject_out}/smoothed_warped_PIB.nii.gz'
	smoothed_pib = ants.smooth_image(warped_pib, 3)
	ants.image_write(smoothed_pib, smoothed_warped_pib_file)

	# Smoothing FEOBV
	smoothed_warped_feobv_file = f'{subject_out}/smoothed_warped_FEOBV.nii.gz'
	smoothed_feobv = ants.smooth_image(warped_feobv, 3)
	ants.image_write(smoothed_feobv, smoothed_warped_feobv_file)
