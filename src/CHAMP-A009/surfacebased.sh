#!/bin/bash


in_dir='/INPUTS'
out_dir='/OUTPUTS/DATA'
source='/REPO/src/CHAMP-A009'

mkdir -p $out_dir

fsdg_file_dlpfc='/OUTPUTS/dlpfc_fsdg.fsgd'
fsdg_file_ppc='/OUTPUTS/ppc_fsdg.fsdg'
matrix_file="${source}/matrix.mtx"

#cp fsaverage to inputs
cp -r /usr/local/freesurfer/subjects/fsaverage /INPUTS/


# for each subject sample mgx vol to left and right hemisphere

for subject in $in_dir/*; do
    echo $subject
    subject_name=$(basename $subject)
    mkdir -p $out_dir/$subject_name

    sub_feobv=$in_dir/$subject_name/assessors/*/*FEOBVQA_v4*/SUBJ/gtmpvc.esupravwm.output
    sub_surf=$subject_name/assessors/*/*FEOBVQA_v4*/SUBJ

    echo "Processing: $sub_feobv"

    mri_vol2surf \
    --mov $sub_feobv/mgx.ctxgm.nii.gz \
    --reg $sub_feobv/aux/bbpet2anat.lta \
    --hemi lh \
    --projfrac 0.5 \
    --o $out_dir/$subject_name/lh.mgx.ctx.fsaverage.sm00.nii.gz \
    --cortex \
    --trgsubject fsaverage \
    --srcsubject $sub_surf \
    --sd $in_dir

    mri_vol2surf \
    --mov $sub_feobv/mgx.ctxgm.nii.gz \
    --reg $sub_feobv/aux/bbpet2anat.lta \
    --hemi rh \
    --projfrac 0.5 \
    --o $out_dir/$subject_name/rh.mgx.ctx.fsaverage.sm00.nii.gz \
    --cortex \
    --trgsubject fsaverage \
    --srcsubject $sub_surf \
    --sd $in_dir


done

#concat all subs into one stack file
echo "Concatenating all left hemispheres"
mri_concat \
--i $out_dir/*/lh.mgx.ctx.fsaverage.sm00.nii.gz \
--o $out_dir/all.lh.mgx.ctx.fsaverage.sm00.nii.gz

echo "Concatenating all right hemispheres"
mri_concat \
--i $out_dir/*/rh.mgx.ctx.fsaverage.sm00.nii.gz \
--o $out_dir/all.rh.mgx.ctx.fsaverage.sm00.nii.gz


#smooth onto surface
echo "Smoothing left hemisphere"
mris_fwhm \
--smooth-only \
--i $out_dir/all.lh.mgx.ctx.fsaverage.sm00.nii.gz \
--o $out_dir/all.lh.mgx.ctx.fsaverage.sm05.nii.gz \
--cortex \
--s fsaverage \
--hemi lh \
--fwhm 5

echo "Smoothing right hemisphere"
mris_fwhm \
--smooth-only \
--i $out_dir/all.rh.mgx.ctx.fsaverage.sm00.nii.gz \
--o $out_dir/all.rh.mgx.ctx.fsaverage.sm05.nii.gz \
--cortex \
--s fsaverage \
--hemi rh \
--fwhm 5

#run mri_glm_fit for dlpfc
echo "Running mri_glm_fit for left hemisphere for dlpfc"
mri_glmfit \
--y $out_dir/all.lh.mgx.ctx.fsaverage.sm05.nii.gz \
--fsdg $fsdg_file_dlpfc \
--C $matrix_file \
--surf fsaverage lh \
--cortex \
--glmdir $out_dir/glm/lh.glm.glmdir_dlpfc

echo "Running mri_glm_fit for right hemisphere for dlpfc"
mri_glmfit \
--y $out_dir/all.rh.mgx.ctx.fsaverage.sm05.nii.gz \
--fsdg $fsdg_file_dlpfc \
--C $matrix_file \
--surf fsaverage rh \
--cortex \
--glmdir $out_dir/glm/rh.glm.glmdir_dlpfc

#run with clusterwise corrections for negative correlations for dlpfc
echo "Running mri_glmfit-sim for left hemisphere for dlpfc"
mri_glmfit-sim \
--glmdir $out_dir/glm/lh.glm.glmdir_dlpfc \
--mczim 2.3 neg \
--2spaces

echo "Running mri_glmfit-sim for right hemisphere for dlpfc"
mri_glmfit-sim \
--glmdir $out_dir/glm/rh.glm.glmdir_dlpfc \
--mczim 2.3 neg \
--2spaces

#run mri_glm_fit for ppc
echo "Running mri_glm_fit for left hemisphere for ppc"
mri_glmfit \
--y $out_dir/all.lh.mgx.ctx.fsaverage.sm05.nii.gz \
--fsdg $fsdg_file_ppc \
--C $matrix_file \
--surf fsaverage lh \
--cortex \
--glmdir $out_dir/glm/lh.glm.glmdir_ppc

echo "Running mri_glm_fit for right hemisphere for ppc"
mri_glmfit \
--y $out_dir/all.rh.mgx.ctx.fsaverage.sm05.nii.gz \
--fsdg $fsdg_file_ppc \
--C $matrix_file \
--surf fsaverage rh \
--cortex \
--glmdir $out_dir/glm/rh.glm.glmdir_ppc

#run with clusterwise corrections for negative correlations for ppc
echo "Running mri_glmfit-sim for left hemisphere for ppc"
mri_glmfit-sim \
--glmdir $out_dir/glm/lh.glm.glmdir_ppc \
--mczim 2.3 neg \
--2spaces

echo "Running mri_glmfit-sim for right hemisphere for ppc"
mri_glmfit-sim \
--glmdir $out_dir/glm/rh.glm.glmdir_ppc \
--mczim 2.3 neg \
--2spaces





