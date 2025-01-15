import glob
import os
import antspynet
import ants
from antspynet import brain_extraction
from nilearn import datasets
import nibabel as nib
from nilearn import image
from scipy.ndimage import binary_dilation


in_dir = '/INPUTS'
atlas_ni = datasets.load_mni152_template()
out_dir = '/OUTPUTS/DATA'


# Convert atlas_file to ants image fixed target for registration
os.makedirs(out_dir)
nib.save(atlas_ni, f'{out_dir}/atlasni.nii.gz')
atlas=f'{out_dir}/atlasni.nii.gz'
fixed = ants.image_read(atlas)

#set cerebellum label
cerebellum_label = 6

for subject in sorted(os.listdir(in_dir)):
	if subject.startswith('.'):
		# ignore hidden files and other junk
		continue
	if subject.startswith('covariates'):
		# ignore covariates csv
		continue

	subject_feobv = glob.glob(f'{in_dir}/{subject}/assessors/*FEOBVQA_v4*')[0]

	print('FEOBV:', subject_feobv)

	subject_out = f'{out_dir}/{subject}'

	os.makedirs(subject_out)

	# Get full file path to input images
	orig_file = f'{subject_feobv}/mri/orig.mgz'
	feobv_file =  f'{subject_feobv}/gtmpvc.esupravwm.output/rbv.nii.gz'
	
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

	# Apply transform to FEOBV image which is already in same space
	warped_feobv_file = f'{subject_out}/warped_FEOBV.nii.gz'
	feobv = ants.image_read(feobv_file)
	warped_feobv = ants.apply_transforms(fixed, feobv, reg['fwdtransforms'])
	ants.image_write(warped_feobv, warped_feobv_file)

	# Smoothing FEOBV
	smoothed_warped_feobv_file = f'{subject_out}/smoothed_warped_FEOBV.nii.gz'
	smoothed_feobv = ants.smooth_image(warped_feobv, 3)
	ants.image_write(smoothed_feobv, smoothed_warped_feobv_file)

	# segment cerebellum
	mri_mni = ants.image_read(warped_orig_file)
	segmentation = antspynet.deep_atropos(mri_mni, do_preprocessing=False)
	cerebellum_mask_data = (segmentation['segmentation_image'].numpy() == cerebellum_label).astype(int)

	# Re-create the cerebellum mask image with correct spatial metadata
	cerebellum_mask = ants.from_numpy(
		cerebellum_mask_data,
		origin=segmentation['segmentation_image'].origin,
		spacing=segmentation['segmentation_image'].spacing,
		direction=segmentation['segmentation_image'].direction
	)

	cerebellum_mask_data = binary_dilation(cerebellum_mask_data)
	# Save the cerebellum mask
	cerebellum_mask.to_filename(f'{subject_out}/cerebellum_mask_deep_atropos.nii.gz')

#mask based on SUVR >1

image_paths = [
	f'{out_dir}/{subject}/smoothed_warped_feobv.nii.gz' for subject in sorted(os.listdir(out_dir))
	if not subject.startswith('.') and not subject.startswith('covariates')
]

averaged_feobv = image.mean_img(image_paths)

group_average_image = f'{out_dir}/averaged_feobv.nii.gz'
averaged_feobv.to_filename(group_average_image)

averaged_data = averaged_feobv.get_fdata()
mask_data = (averaged_data > 1).astype(int)

# Save the mask as a new NIfTI image
from nilearn.image import new_img_like
mask_image = new_img_like(averaged_feobv, mask_data)
mask_file_path = f'{out_dir}/averaged_feobv_mask.nii.gz'
mask_image.to_filename(mask_file_path)
