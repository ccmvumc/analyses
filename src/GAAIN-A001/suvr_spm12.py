from nipype.interfaces.io import SelectFiles, DataSink
from nipype.interfaces.spm import NewSegment, Normalize12, Coregister
from nipype import Node, Workflow
import ants
import os
from os.path import join as opj
from nipype import IdentityInterface
import glob
from nilearn import image, masking, plotting
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import multiprocessing
from antspynet import brain_extraction
from nilearn.image import resample_to_img

from nipype.interfaces.matlab import MatlabCommand
MatlabCommand.set_default_paths('/Users/jasonrussell/Documents/MATLAB/spm12')

if not os.path.exists('/Users/jasonrussell/Documents/OUTPUTS/gaain_validation_spm12'):
	os.mkdir('/Users/jasonrussell/Documents/OUTPUTS/gaain_validation_spm12')
else:
	print('Directory exists, continue')

in_dir = '/Users/jasonrussell/Documents/INPUTS/gaain'
out_dir = '/Users/jasonrussell/Documents/OUTPUTS/gaain_validation_spm12'
atlas = f'{in_dir}/atlases/avg152T1.nii'
ctx_voi = f'{in_dir}/atlases/voi_ctx_2mm.nii'
wcbm_voi = f'{in_dir}/atlases/voi_WhlCbl_2mm.nii'

#import ants atlas
mni = ants.image_read(atlas)

subject_list = []


for subject in sorted(os.listdir(f'{in_dir}/scans')):
		if subject.startswith('.'):
			# ignore hidden files and other junk
			continue
		
		if subject.startswith('cov'):
			# ignore covariates
			continue
		
		#ignore atlases
		if subject.startswith('spm'):
			continue
		if subject.startswith('centiloid'):
			continue
		
		subject_list.append(subject)
		
		subject_amyloid = glob.glob(f'{in_dir}/scans/{subject}/PET/*PiB*')[0]
		subject_mr = glob.glob(f'{in_dir}/scans/{subject}/MR/*MR*')[0]
	
		print('Amyloid:', subject_amyloid)
	
		subject_out = f'{out_dir}/{subject}'
		
		if not os.path.exists(subject_out):
			os.mkdir(subject_out)
		else:
			print('Directory exists, continue')
	
		# Get full file path to input images
		orig_file = subject_mr
		amyloid_file = subject_amyloid
		
		# Skull Strip Original T1 and mask
		raw = ants.image_read(orig_file)
		raw_pet = ants.image_read(amyloid_file)
		
		# Skull Strip Original T1
		#extracted_mask = brain_extraction(raw, modality='t1')
		
		#Apply mask with skull stripped
		#masked_image = ants.mask_image(raw, extracted_mask)
		
		moving = raw
		
		#warp PET to MR
		warp_pet = ants.registration(moving, raw_pet, type_of_transform='Rigid')
	
		# Do Registration of Moving to Fixed
		reg = ants.registration(mni, moving, type_of_transform='Rigid')
	
		# Save warped orig
		warped_orig_file = f'{subject_out}/reorient_mr.nii'
		ants.image_write(reg['warpedmovout'], warped_orig_file)
	
		# Apply transform to amyloid image which is already in same space
		warped_amyloid_file = f'{subject_out}/reorient_pet.nii'
		amyloid = warp_pet['warpedmovout']
		warped_amyloid = ants.apply_transforms(mni, amyloid, reg['fwdtransforms'])
		ants.image_write(warped_amyloid, warped_amyloid_file)
		


infosource = Node(IdentityInterface(fields=['subject_id']), name="infosource")
infosource.iterables = [('subject_id', subject_list)]

anat_file = opj('{subject_id}','reorient_mr.nii')
func_file = opj('{subject_id}','reorient_pet.nii')

templates = {
	'anat': anat_file,
	'func': func_file
	}

selectfiles = Node(SelectFiles(templates, 
							   base_directory= out_dir),
				   name="selectfiles")


# coreg
coreg_mr = Node(Coregister(), name="coreg_mr")
coreg_mr.jobtype = 'estwrite'
coreg_mr.inputs.target = atlas

coreg_pet = Node(Coregister(), name='coreg_pet')
coreg_pet.jobtype = 'estwrite'
coreg_pet.nonlinear_regularization = 1

#segmentation


tpm_img = '/Users/jasonrussell/Documents/MATLAB/spm12/tpm/TPM.nii'
tissue1 = ((tpm_img, 1), 1, (True, False), (False, False))
tissue2 = ((tpm_img, 2), 1, (True, False), (False, False))
tissue3 = ((tpm_img, 3), 2, (True, False), (False, False))
tissue4 = ((tpm_img, 4), 3, (False, False), (False, False))
tissue5 = ((tpm_img, 5), 4, (False, False), (False, False))
tissue6 = ((tpm_img, 6), 2, (False, False), (False, False))
tissues = [tissue1, tissue2, tissue3, tissue4, tissue5, tissue6]

segmentation = Node(NewSegment(tissues=tissues, write_deformation_fields=[True, True]), name="segmentation")

nan = float('nan')

#normalization
norm_write = Node(Normalize12(), name = "norm_write")
norm_write.inputs.jobtype = 'write'
norm_write.inputs.write_bounding_box = [[nan, nan, nan], [nan, nan, nan]]

#datasink
datasink = Node(DataSink(base_directory=out_dir),
				name = 'datasink')

#make workflow
cl_preproc = Workflow(name='cl_preproc', base_dir = out_dir)

cl_preproc.connect([
	(infosource, selectfiles, [('subject_id', 'subject_id')]),
	(selectfiles, coreg_mr, [('anat', 'source')]),
	(selectfiles, coreg_mr, [('anat', 'apply_to_files')]),
	(selectfiles, coreg_pet, [('func', 'source')]),
	(selectfiles, coreg_pet, [('func', 'apply_to_files')]),
	(coreg_mr, coreg_pet, [('coregistered_files', 'target')]),
	(coreg_mr, segmentation, [('coregistered_files', 'channel_files')]),
	(segmentation, norm_write, [('forward_deformation_field', 'deformation_file')]),
	#(coreg_pet, norm_write, [('coregistered_files', 'image_to_align')]),
	(coreg_pet, norm_write, [('coregistered_files', 'apply_to_files')]),
	(coreg_mr, datasink, [('coregistered_files', 'normalized_mr1')]),
	(coreg_pet, datasink, [('coregistered_files', 'normalized_pet1')]),
	(norm_write, datasink, [('normalized_files', 'normalized_final')])
])

if __name__ == '__main__':
	multiprocessing.set_start_method('fork')
	cl_preproc.run('MultiProc', plugin_args={'n_procs': 12})

cl_preproc.write_graph(graph2use='exec', format='png', simple_form=False)

#calculate SUVR and apply to df

# suvr_value = ctx_stats.result.outputs.out_stat / wcbm_stats.result.outputs.out_stat
output_df = pd.DataFrame(columns=['ID', 'SUVR'])

for subject in sorted(os.listdir(f'{out_dir}/normalized_final')):
	#apply masks
	pet_mni = f'{out_dir}/normalized_final/{subject}/wrreorient_pet.nii'
	
	# Resample the mask to match the image affine
	resampled_ctx_voi = resample_to_img(ctx_voi, pet_mni, interpolation='nearest')
	resampled_wcbm_voi = resample_to_img(wcbm_voi, pet_mni, interpolation='nearest')
	
	ctx_masked = masking.apply_mask(pet_mni, resampled_ctx_voi)
	wcbm_masked = masking.apply_mask(pet_mni, resampled_wcbm_voi)
	
	# Calculate the mean uptake in the VOIs
	mean_uptake_voi = ctx_masked.mean()
	mean_uptake_ref = wcbm_masked.mean()
	
	suvr = mean_uptake_voi/mean_uptake_ref
	
	subject_name = subject.split('_')[-1]
	row = [subject_name, suvr]
	
	output_df.loc[len(output_df)] = row
	
# Generate pdf report
pdf_filename = f"{out_dir}/report.pdf"

with PdfPages(pdf_filename) as pdf:
	for subject in sorted(os.listdir(f'{out_dir}/normalized_final')):
		fig, axs = plt.subplots(3, 1, figsize=(10,14))
		subject_name = subject.split('_')[-1]
		
		img = image.load_img(f'{out_dir}/normalized_final/{subject}/wrreorient_pet.nii')
		
		plotting.plot_roi(
			img,
			figure=fig,
			title = f"{subject_name} PET transform to MNI",
			axes=axs[0]
		)
		
		plotting.plot_roi(
			ctx_voi,
			img,
			figure=fig,
			title = f"{subject_name} PET transform with ctx VOI overlay",
			axes=axs[1]
		)
		
		plotting.plot_roi(
			wcbm_voi,
			img,
			figure=fig,
			title = f"{subject_name} PET transform with cblm VOI overlay",
			axes=axs[2]
		)
		
		pdf.savefig(fig, dpi=300)
		plt.close(fig)
	
output_df.to_csv(f'{out_dir}/standard_centiloid_suvrs.csv', index=False)


