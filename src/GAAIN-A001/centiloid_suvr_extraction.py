# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""


import os
import ants
from nilearn import image, masking, plotting
import nibabel as nib
import pandas as pd
import glob
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

in_dir = '/INPUTS'
atlas = '/REPO/spm8_MNI_avg152T1.nii'
out_dir = '/OUTPUTS/DATA'


os.makedirs(out_dir)

#Open atlas
mni = ants.image_read(atlas)

# Import gaain masks 
ctx_voi = image.load_img(
	'/REPO/centiloid_ctx_2mm.nii'
	)

wcbm_voi = image.load_img(
	'/REPO/centiloid_WhlCbl_2mm.nii'
	)


fixed = mni

output_df = pd.DataFrame(columns=['ID', 'SUVR'])

# Generate pdf report
pdf_filename = f"{out_dir}/Centiloid warping validation.pdf"

with PdfPages(pdf_filename) as pdf:
	for subject in sorted(os.listdir(in_dir)):
		if subject.startswith('.'):
			# ignore hidden files and other junk
			continue
	
		subject_amyloid = glob.glob(f'{in_dir}/{subject}/*PiB*')
		subject_mr = glob.glob(f'{in_dir}/{subject}/*MR*')
	
		print('Amyloid:', subject_amyloid)
	
		subject_out = f'{out_dir}/{subject}'
	
		os.makedirs(subject_out)
	
		# Get full file path to input images
		orig_file = subject_mr
		amyloid_file = subject_amyloid
		
		# Skull Strip Original T1 and mask
		raw = ants.image_read(orig_file)
		raw_pet = ants.image_read(amyloid_file)
		#mri_strip_mask = brain_extraction(raw, modality='t1')
		
		#print orientation of PET and MRI
		pet_img = nib.load(subject_amyloid)
		mr_img = nib.load(subject_mr)
		
		current_ornt_pet = nib.aff2axcodes(pet_img.affine)
		current_ornt_mri = nib.aff2axcodes(mr_img.affine)
		
		print(f'PET image orientation: {current_ornt_pet}')
		print(f'MRI image orientation: {current_ornt_mri}')
		
		# Load orig T1 image as moving image for registration
		moving = raw
		
		#warp PET to MR
		warp_pet = ants.registration(moving, raw_pet, type_of_transform='SyN')
	
		# Do Registration of Moving to Fixed
		reg = ants.registration(fixed, moving, type_of_transform='SyN')
	
		# Save warped orig
		warped_orig_file = f'{subject_out}/warped_orig.nii.gz'
		ants.image_write(reg['warpedmovout'], warped_orig_file)
	
		# Apply transform to amyloid image which is already in same space
		warped_amyloid_file = f'{subject_out}/warped_amyloid.nii.gz'
		amyloid = warp_pet['warpedmovout']
		warped_amyloid = ants.apply_transforms(fixed, amyloid, reg['fwdtransforms'])
		ants.image_write(warped_amyloid, warped_amyloid_file)
		
		#import image as nifti1
		xformed_PET = image.load_img(f'{subject_out}/warped_amyloid.nii.gz')
		
		resampled_PET = image.resample_to_img(xformed_PET, ctx_voi)
		
		#apply masks
		ctx_masked = masking.apply_mask(resampled_PET, ctx_voi)
		wcbm_masked = masking.apply_mask(resampled_PET, wcbm_voi)
		
		# Calculate the mean uptake in the VOIs
		mean_uptake_voi = ctx_masked.mean()
		mean_uptake_ref = wcbm_masked.mean()
		
		suvr = mean_uptake_voi/mean_uptake_ref
		
		row = [subject, suvr]
		
		output_df.loc[len(output_df)] = row
		
		fig, axs = plt.subplots(3, 1, figsize=(10,14))
		
		plotting.plot_stat_map(
			xformed_PET,
			colorbar=False,
			figure=fig,
			title = f"{subject} PET transform /n PET image orientation: {current_ornt_pet} /n MRI image orientation: {current_ornt_mri}",
			axes=axs[0]
		)
		
		plotting.plot_stat_map(
			resampled_PET,
			colorbar=False,
			figure=fig,
			title = f"{subject} PET transform and resampled",
			axes=axs[1]
		)
		
		axs[2].annotate(
			f'PET image orientation: {current_ornt_pet} \n MRI image orientation: {current_ornt_mri}',
			(0.1, 0.5), xycoords='axes fraction', 
			va='center'
			)
		
		axs[2].axis('off')
		
		pdf.savefig(fig, dpi=300)
		plt.close(fig)
	
output_df.to_csv(f'{out_dir}/standard_centiloid_suvrs.csv', index=False)



