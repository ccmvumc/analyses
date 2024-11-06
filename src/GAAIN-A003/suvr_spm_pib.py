from nipype.interfaces.io import SelectFiles, DataSink
from nipype.interfaces.spm import Segment, Normalize, Coregister
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

from nipype.interfaces.matlab import MatlabCommand
MatlabCommand.set_default_paths('/Users/jasonrussell/Documents/MATLAB/spm12')

if not os.path.exists('/Users/jasonrussell/Documents/OUTPUTS/gaain_A003/pib'):
	os.mkdir('/Users/jasonrussell/Documents/OUTPUTS/gaain_A003/pib')
else:
	print('Directory exists, continue')

in_dir = '/Users/jasonrussell/Documents/INPUTS/gaain_A003'
out_dir = '/Users/jasonrussell/Documents/OUTPUTS/gaain_A003'
atlas = f'{in_dir}/atlases/avg152T1.nii'
ctx_voi = f'{in_dir}/atlases/voi_ctx_2mm.nii'
wcbm_voi = f'{in_dir}/atlases/voi_WhlCbl_2mm.nii'

#import ants atlas
mni = ants.image_read(atlas)

subject_list = []


for subject in sorted(os.listdir(out_dir)):
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
		#ignore folders
		if subject.startswith('av45'):
			continue
		if subject.startswith('pib'):
			continue
		
		subject_list.append(subject)
		
		subject_amyloid = f'{out_dir}/{subject}/pib/mean_pet_pib.nii.gz'
		subject_mr = glob.glob(f'{out_dir}/{subject}/mr/*mr.nii')[0]
	
		print('Amyloid:', subject_amyloid)
	
		subject_out = f'{out_dir}/pib/{subject}'
		
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
	
base_dir = f'{out_dir}/pib'

selectfiles = Node(SelectFiles(templates, 
							   base_directory= base_dir),
				   name="selectfiles")


# coreg
coreg_mr = Node(Coregister(), name="coreg_mr")
coreg_mr.jobtype = 'estwrite'
coreg_mr.inputs.target = atlas

coreg_pet = Node(Coregister(), name='coreg_pet')
coreg_pet.jobtype = 'estwrite'
coreg_pet.nonlinear_regularization = 1

#segmentation
segmentation = Node(Segment(), name="segmentation")

nan = float('nan')

#normalization
norm_write = Node(Normalize(), name = "norm_write")
norm_write.inputs.jobtype = 'write'
norm_write.inputs.write_bounding_box = [[nan, nan, nan], [nan, nan, nan]]
norm_write.inputs.write_voxel_sizes = [2, 2, 2]

#datasink
datasink = Node(DataSink(base_directory=base_dir),
				name = 'datasink')

#make workflow
cl_preproc = Workflow(name='cl_preproc', base_dir = base_dir)

cl_preproc.connect([
	(infosource, selectfiles, [('subject_id', 'subject_id')]),
	(selectfiles, coreg_mr, [('anat', 'source')]),
	(selectfiles, coreg_mr, [('anat', 'apply_to_files')]),
	(selectfiles, coreg_pet, [('func', 'source')]),
	(selectfiles, coreg_pet, [('func', 'apply_to_files')]),
	(coreg_mr, coreg_pet, [('coregistered_files', 'target')]),
	(coreg_mr, segmentation, [('coregistered_files', 'data')]),
	(segmentation, norm_write, [('transformation_mat', 'parameter_file')]),
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

for subject in sorted(os.listdir(f'{out_dir}/pib/normalized_final')):
	#apply masks
	pet_mni = f'{out_dir}/pib/normalized_final/{subject}/wrreorient_pet.nii'
	
	ctx_masked = masking.apply_mask(pet_mni, ctx_voi)
	wcbm_masked = masking.apply_mask(pet_mni, wcbm_voi)
	
	# Calculate the mean uptake in the VOIs
	mean_uptake_voi = ctx_masked.mean()
	mean_uptake_ref = wcbm_masked.mean()
	
	suvr = mean_uptake_voi/mean_uptake_ref
	
	subject_name = subject.split('_subject_id_')[1]
	row = [subject_name, suvr]
	
	output_df.loc[len(output_df)] = row
	
# Generate pdf report
pdf_filename = f"{out_dir}/pib/report.pdf"

with PdfPages(pdf_filename) as pdf:
	for subject in sorted(os.listdir(f'{out_dir}/pib/normalized_final')):
		fig, axs = plt.subplots(3, 1, figsize=(10,14))
		subject_name = subject.split('_subject_id_')[1]
		
		img = image.load_img(f'{out_dir}/pib/normalized_final/{subject}/wrreorient_pet.nii')
		
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
	
output_df.to_csv(f'{out_dir}/pib_centiloid_suvrs.csv', index=False)


