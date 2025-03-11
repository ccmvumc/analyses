mkdir /OUTPUTS/SUBJECTS

cd /INPUTS

for i in */;do 
	echo $i
	mkdir -p /OUTPUTS/SUBJECTS/$i

	# Convert to NIFTI from FreeSurfer
	mri_convert /INPUTS/${i}/*/assessors/*/mri/orig.mgz /OUTPUTS/SUBJECTS/${i}/orig.nii.gz

	# Convert to NIFTI
	mri_convert /INPUTS/${i}/*/assessors/*/ThalamicNuclei.FSvoxelSpace.mgz /OUTPUTS/SUBJECTS/${i}/ThalamicNuclei.FSvoxelSpace.nii.gz

	# Already NIFTI, just copy
	cp /INPUTS/${i}/*/assessors/*/thomas* /OUTPUTS/SUBJECTS/${i}/
done

echo "DONE!"
