export SUBJECTS_DIR=/OUTPUTS/DATA/SUBJECTS

cd $SUBJECTS_DIR


# Get esupravwm volume
# NOTE: esupravwm is result of this command: mri_binarize --i mri/wmparc.mgz 
# --match 
# 3003 3017 3022 3024 3027 3028 3029 3031 4003 4017 4022 4024 4027 4028 4029 4031 \
# --erode 1 --o esupravwm.nii.gz;

set -x

for i in *;do
	echo $i

    cd ${SUBJECTS_DIR}/${i}

    mri_segstats --seg esupravwm.nii.gz --i esupravwm.nii.gz --id 1 --sumwf esupravwm.volume.txt

done

echo DONE
