from nipype.interfaces.io import SelectFiles, DataSink
from nipype.interfaces.spm import Segment, Normalize, Coregister
from nipype import Node, Workflow
import ants
import os
from os.path import join as opj
from nipype import IdentityInterface
from nipype.interfaces.fsl import ImageStats
import glob

from nipype.interfaces.matlab import MatlabCommand
MatlabCommand.set_default_paths('/home/jason/matlab_pkg/spm8')

if not os.path.exists('/home/jason/OUTPUTS/gaain_validation'):
	os.mkdir('/home/jason/OUTPUTS/gaain_validation')
else:
	print('Directory exists, continue')

in_dir = '/home/jason/INPUTS/gaain_sample'
out_dir = '/home/jason/OUTPUTS/gaain_validation'
atlas = f'{in_dir}/atlases/spm8_MNI_avg152T1.nii'
ctx_voi = f'{in_dir}/atlases/centiloid_ctx_2mm.nii'
wcbm_voi = f'{in_dir}/atlases/centiloid_WhlCbl_2mm.nii'

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
		#mri_strip_mask = brain_extraction(raw, modality='t1')
		
		# Load orig T1 image as moving image for registration
		moving = raw
		
		#move MR to atlas
		reorient_mr = ants.registration(moving, mni, type_of_transform = 'Rigid')
		
		#move PET to MR
		reorient_pet = ants.registration(raw_pet, reorient_mr['warpedmovout'], type_of_transform='Rigid')
		
		# Save reorient mr
		warped_mr_file = f'{subject_out}/reorient_mr.nii'
		ants.image_write(reorient_mr['warpedmovout'], warped_mr_file)
		
		# Save reorient PET
		warped_pet_file = f'{subject_out}/reorient_pet.nii'
		ants.image_write(reorient_pet['warpedmovout'], warped_pet_file)
	


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

# #initially overlay images
# overlay_mr = Node(Registration(), name = 'overlay_mr')
# overlay_mr.inputs.fixed_image = atlas
# overlay_mr.inputs.metric = ['CC']
# overlay_mr.inputs.transforms = ['Rigid']
# overlay_mr.inputs.transform_parameters = [(0.1,)]
# overlay_mr.inputs.smoothing_sigmas = [[4.0, 2.0, 1.0, 0.0]]
# overlay_mr.inputs.shrink_factors = [[8, 4, 2, 1]]
# overlay_mr.inputs.convergence_threshold = [1e-6]
# overlay_mr.inputs.number_of_iterations = [[1000, 500, 250, 100]] 

# overlay_pet = Node(Registration(), name = 'overlay_pet')
# overlay_pet.inputs.metric = ['MeanSquares']
# overlay_pet.inputs.transforms = ['Rigid']
# overlay_mr.inputs.transform_parameters = [(0.1,)]
# overlay_pet.inputs.smoothing_sigmas = [[4.0, 2.0, 1.0, 0.0]]
# overlay_pet.inputs.shrink_factors = [[8, 4, 2, 1]]
# overlay_pet.inputs.convergence_threshold = [1e-6]
# overlay_pet.inputs.number_of_iterations = [[1000, 500, 250, 100]] 

# coreg
coreg_mr = Node(Coregister(), name="coreg_mr")
coreg_mr.jobtype = 'estwrite'
coreg_mr.inputs.target = atlas

coreg_pet = Node(Coregister(), name='coreg_pet')
coreg_pet.jobtype = 'estwrite'
coreg_pet.nonlinear_regularization = 1

# segmentation
#tpm_csf = '/home/jason/matlab_pkg/spm8/tpm/csf.nii'
#tpm_gm = '/home/jason/matlab_pkg/spm8/tpm/grey.nii'
#tpm_wm = '/home/jason/matlab_pkg/spm8/tpm/white.nii'
#tissue1 = ((tpm_gm, 1), 1, (True, False), (False, False))  # Gray matter
#tissue2 = ((tpm_wm, 1), 1, (True, False), (False, False))  # White matter
#tissue3 = ((tpm_csf, 1), 1, (True, False), (False, False))  # CSF
#tissues = [tissue1, tissue2, tissue3]

segmentation = Node(Segment(), name="segmentation")


#normalization
norm_write = Node(Normalize(), name = "norm_write")
norm_write.jobtype = 'write'
norm_write.source_image_smoothing = 8
norm_write.affine_regularization = 'mni'
norm_write.DCT_period_cutoff = 25
norm_write.nonlinear_iterations = 16
norm_write.nonlinear_regularization = 1
norm_write.write_bounding_box = [[-90, -126, -72], [91, 91, 109]]
norm_write.write_voxel_sizes = [2, 2, 2]


#calculate SUVRs in each VOI
ctx_stats = Node(ImageStats(), name = 'ctx_stats')
ctx_stats.mask_file = ctx_voi
ctx_stats.op_string = '-M'

wcbm_stats = Node(ImageStats(), name = 'wcbm_stats')
wcbm_stats.mask_file = wcbm_voi
wcbm_stats.op_string = '-M'

#datasink
datasink = Node(DataSink(base_directory='/home/jason/OUTPUTS/gaain_validation'),
				name = 'datasink')

#make workflow
cl_preproc = Workflow(name='cl_preproc', base_dir = '/home/jason/OUTPUTS/gaain_validation')

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
	(norm_write, ctx_stats, [('normalized_files', 'in_file' )]),
	(norm_write, wcbm_stats, [('normalized_files', 'in_file')]),
	(coreg_mr, datasink, [('coregistered_files', 'normalized_mr1')]),
	(coreg_pet, datasink, [('coregistered_files', 'normalized_pet1')]),
	(norm_write, datasink, [('normalized_files', 'normalized_final')])
])

cl_preproc.run('MultiProc', plugin_args={'n_procs': 8})

#calculate SUVR and apply to df

suvr_value = ctx_stats.result.outputs.out_stat / wcbm_stats.result.outputs.out_stat



