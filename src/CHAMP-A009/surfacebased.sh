#!/bin/bash


in_dir='/INPUTS'
out_dir='/OUTPUTS/DATA'
source='/REPO/src/CHAMP-A009'

mkdir -p $out_dir

fsdg_file='/OUTPUTS/g1v2.fsgd'
matrix_file="${source}/matrix.mtx"


# for each subject sample mgx vol to left and right hemisphere

for subject in $in_dir/*; do
    echo $subject
    subject_name=$(basename $subject)
    mkdir -p $out_dir/$subject_name

    sub_feobv=$in_dir/$subject_name/assessors/*FEOBVQA_v4*/gtmpvc.esupravwm.output

    echo "Processing: $sub_feobv"

    mri_vol2surf \
    --mov $sub_feobv/mgx.ctxgm.nii.gz \
    --reg $sub_feobv/aux/bbpet2anat.lta \
    --hemi lh \
    --projfrac 0.5 \
    --o $out_dir/$subject_name/lh.mgx.ctx.fsaverage.sm00.nii.gz \
    --cortex \
    --trgsubject fsaverage

    mri_vol2surf \
    --mov $sub_feobv/mgx.ctxgm.nii.gz \
    --reg $sub_feobv/aux/bbpet2anat.lta \
    --hemi rh \
    --projfrac 0.5 \
    --o $out_dir/$subject_name/rh.mgx.ctx.fsaverage.sm00.nii.gz \
    --cortex \
    --trgsubject fsaverage


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

#run mri_glm_fit
echo "Running mri_glm_fit for left hemisphere"
mri_glmfit \
--y $out_dir/all.lh.mgx.ctx.fsaverage.sm05.nii.gz \
--fsdg $fsdg_file \
--C $matrix_file \
--surf fsaverage lh \
--cortex \
--glmdir $out_dir/glm/lh.glm.glmdir

echo "Running mri_glm_fit for right hemisphere"
mri_glmfit \
--y $out_dir/all.rh.mgx.ctx.fsaverage.sm05.nii.gz \
--fsdg $fsdg_file \
--C $matrix_file \
--surf fsaverage rh \
--cortex \
--glmdir $out_dir/glm/rh.glm.glmdir

#run with clusterwise corrections for negative correlations
echo "Running mri_glmfit-sim for left hemisphere"
mri_glmfit-sim \
--glmdir $out_dir/glm/lh.glm.glmdir \
--mczim 2.3 neg \
--2spaces

echo "Running mri_glmfit-sim for right hemisphere"
mri_glmfit-sim \
--glmdir $out_dir/glm/rh.glm.glmdir \
--mczim 2.3 neg \
--2spaces





