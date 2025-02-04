import glob
import os
from scipy.ndimage import binary_dilation
import ants
from antspynet import brain_extraction
import antspynet
from nilearn import datasets
from nilearn import image, masking
from nilearn.image import math_img
import nibabel as nib
from config import in_dir, out_dir

atlas = '/Users/jasonrussell/Documents/code/analyses_local/atlases'
atlas_ni = datasets.load_mni152_template()

# Convert atlas_file to ants image fixed target for registration
nib.save(atlas_ni, f'{out_dir}/atlasni.nii.gz')
atlas_mni=f'{out_dir}/atlasni.nii.gz'

# Convert atlas_file to ants image fixed target for registration
atlas=f'{atlas}/CS_DS_Intensity.nii.gz'
fixed_mni = ants.image_read(atlas_mni)
fixed_ds = ants.image_read(atlas)

#set cerebellum label
cerebellum_label = 6

for subject in sorted(os.listdir(in_dir)):
	if subject.startswith('.'):
		# ignore hidden files and other junk
		continue
	if subject.startswith('covariates'):
		# ignore covariates csv
		continue

	subject_feobv = glob.glob(f'{in_dir}/{subject}')[0]

	print('FEOBV:', subject_feobv)

	subject_out = f'{out_dir}/{subject}'

	os.makedirs(subject_out)

	# Get full file path to input images
	orig_file = f'{subject_feobv}/orig.mgz'
	feobv_file =  f'{subject_feobv}/rbv.nii.gz'
	
	# Skull Strip Original T1
	raw = ants.image_read(orig_file)
	extracted_mask = brain_extraction(raw, modality='t1')

	#Apply mask with skull stripped
	masked_image = ants.mask_image(raw, extracted_mask)

	# Load orig T1 image as moving image for registration
	moving = masked_image

	#####MOVE TO MNI FOR CEREBELLAR EXTRACTION, THEN CEREBELLUM BACK TO SUBJECT
	# Do Registration of Moving to Fixed
	reg = ants.registration(fixed_mni, moving, type_of_transform='SyN')

	# Save warped orig
	warped_orig_file = f'{subject_out}/warped_orig_mni.nii.gz'
	ants.image_write(reg['warpedmovout'], warped_orig_file)

	# segment cerebellum
	mri_mni = ants.image_read(warped_orig_file)
	segmentation = antspynet.deep_atropos(mri_mni, do_preprocessing=False)
	cerebellum_mask_data = (segmentation['segmentation_image'].numpy() == cerebellum_label).astype(int)

	cerebellum_mask_data = binary_dilation(cerebellum_mask_data)

	# Re-create the cerebellum mask image with correct spatial metadata
	cerebellum_mask = ants.from_numpy(
		cerebellum_mask_data,
		origin=segmentation['segmentation_image'].origin,
		spacing=segmentation['segmentation_image'].spacing,
		direction=segmentation['segmentation_image'].direction
	)

	# Save the cerebellum mask
	cerebellum_mask.to_filename(f'{subject_out}/cerebellum_mask_deep_atropos_mni.nii.gz')

	# Transform cerebellum to subject
	cerebellum_subj = ants.apply_transforms(moving, cerebellum_mask, reg['invtransforms'])

	# Do Registration of Moving to Fixed (DS)
	reg_ds = ants.registration(fixed_ds, moving, type_of_transform='SyN')

	# Save warped orig
	warped_orig_file = f'{subject_out}/warped_orig.nii.gz'
	ants.image_write(reg_ds['warpedmovout'], warped_orig_file)


	# Apply transform to FEOBV image which is already in same space
	warped_feobv_file = f'{subject_out}/warped_FEOBV.nii.gz'
	feobv = ants.image_read(feobv_file)
	warped_feobv = ants.apply_transforms(fixed_ds, feobv, reg_ds['fwdtransforms'])
	ants.image_write(warped_feobv, warped_feobv_file)

	# Smoothing FEOBV
	smoothed_warped_feobv_file = f'{subject_out}/smoothed_warped_FEOBV.nii.gz'
	smoothed_feobv = ants.smooth_image(warped_feobv, 3)
	ants.image_write(smoothed_feobv, smoothed_warped_feobv_file)

	#transform Cerebellar mask to DS space
	warped_cerebellum_file = f'{subject_out}/cerebellum_mask_deep_atropos.nii.gz'
	warped_cerebellum = ants.apply_transforms(fixed_ds, cerebellum_subj, reg_ds['fwdtransforms'])
	ants.image_write(warped_cerebellum, warped_cerebellum_file)

	#generate GM mask in MNI space
	#resample MRI to same as PET images for mask generation
	pet = image.load_img(f'{subject_out}/smoothed_warped_FEOBV.nii.gz')
	mr = image.load_img(f'{subject_out}/warped_orig_mni.nii.gz')
	resampled_mr = image.resample_to_img(mr, pet)

	#apply nilearn mask
	wb_mask = masking.compute_brain_mask(resampled_mr, mask_type='whole-brain')
	#apply gm mask
	gm_mask = masking.compute_brain_mask(resampled_mr, mask_type='gm')

	whole_brain_without_wm = math_img('img1 * img2', img1=wb_mask, img2=gm_mask)

	#save gm mask in MNI
	whole_brain_without_wm.to_filename(f'{subject_out}/whole_brain_gm_mni.nii.gz')

	#import as ants image
	wb_gm_mni = ants.image_read(f'{subject_out}/whole_brain_gm_mni.nii.gz')

	#warp back to subject space
	wb_no_wm_sub = ants.apply_transforms(moving, wb_gm_mni, reg['invtransforms'])
	wb_no_wm_ds = ants.apply_transforms(fixed_ds, wb_no_wm_sub, reg_ds['fwdtransforms'])

	ants.image_write(wb_no_wm_ds, f'{subject_out}/gm_ds.nii.gz')


#mask based on SUVR >1

image_paths = [
	f'{out_dir}/{subject}/smoothed_warped_feobv.nii.gz' for subject in sorted(os.listdir(out_dir))
	if not subject.startswith('.') and not subject.startswith('covariates') and not subject.startswith('atlas')
	and not subject.startswith('study')
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

