#!/bin/bash


in_dir='/INPUTS'
out_dir='/OUTPUTS/DATA'
source='/REPO/src/CHAMP-A009'

mkdir -p $out_dir
mkdir -p $out_dir/glm

fsgd_file_gfap='/OUTPUTS/gfap.fsgd'
fsgd_file_nfl='/OUTPUTS/nfl.fsgd'
fsgd_file_ab4240='/OUTPUTS/abeta42_40_ratio.fsgd'
fsgd_file_tau='/OUTPUTS/tau.fsgd'
matrix_file="${source}/matrix.mtx"

#cp fsaverage to inputs
cp -r /usr/local/freesurfer/subjects/fsaverage /INPUTS/


# for each subject sample mgx vol to left and right hemisphere

for subject in $in_dir/*; do
    echo $subject
    #skip if subject is not a directory
    if [ ! -d $subject ]; then
        continue
    fi

    #skip if subject is fsaverage
    if [ $subject == "fsaverage" ]; then
        continue
    fi
    
    subject_name=$(basename $subject)
    mkdir -p $out_dir/$subject_name

    sub_feobv=$in_dir/$subject_name/assessors/*/*FEOBVQA_v4*/SUBJ/gtmpvc.esupravwm.output
    sub_surf_w_input=$in_dir/$subject_name/assessors/*/*FEOBVQA_v4*/SUBJ
    
    echo "Before expansion - sub_feobv: $sub_feobv"
    echo "Before expansion - sub_surf_w_input: $sub_surf_w_input"
    
    sub_surf_w_input=$(echo $sub_surf_w_input)

    #select from $sub_surf_w_input the string not including /INPUTS/
    sub_surf=$(echo $sub_surf_w_input | sed "s|$in_dir/||")

    # Expand wildcards to actual paths
    sub_feobv=$(echo $sub_feobv)
    sub_surf=$(echo $sub_surf)
    
    echo "After expansion - sub_feobv: $sub_feobv"
    echo "After expansion - sub_surf: $sub_surf"

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

#run mri_glm_fit for gfap
echo "Running mri_glm_fit for left hemisphere for gfap"
mri_glmfit \
--y $out_dir/all.lh.mgx.ctx.fsaverage.sm05.nii.gz \
--fsgd $fsgd_file_gfap \
--C $matrix_file \
--surf fsaverage lh \
--cortex \
--glmdir $out_dir/glm/lh.glm.glmdir_gfap \
--eres-save

echo "Running mri_glm_fit for right hemisphere for gfap"
mri_glmfit \
--y $out_dir/all.rh.mgx.ctx.fsaverage.sm05.nii.gz \
--fsgd $fsgd_file_gfap \
--C $matrix_file \
--surf fsaverage rh \
--cortex \
--glmdir $out_dir/glm/rh.glm.glmdir_gfap \
--eres-save

#run with clusterwise corrections for negative correlations for gfap
echo "Running mri_glmfit-sim for left hemisphere for gfap"
mri_glmfit-sim \
--glmdir $out_dir/glm/lh.glm.glmdir_gfap \
--perm 1000 4.0 neg \
--cwp 0.05 \
--2spaces \
--bg 1
echo "Running mri_glmfit-sim for right hemisphere for gfap"
mri_glmfit-sim \
--glmdir $out_dir/glm/rh.glm.glmdir_gfap \
--perm 1000 4.0 neg \
--cwp 0.05 \
--2spaces \
--bg 1

#run mri_glm_fit for nfl
echo "Running mri_glm_fit for left hemisphere for nfl"
mri_glmfit \
--y $out_dir/all.lh.mgx.ctx.fsaverage.sm05.nii.gz \
--fsgd $fsgd_file_nfl \
--C $matrix_file \
--surf fsaverage lh \
--cortex \
--glmdir $out_dir/glm/lh.glm.glmdir_nfl \
--eres-save

echo "Running mri_glm_fit for right hemisphere for nfl"
mri_glmfit \
--y $out_dir/all.rh.mgx.ctx.fsaverage.sm05.nii.gz \
--fsgd $fsgd_file_nfl \
--C $matrix_file \
--surf fsaverage rh \
--cortex \
--glmdir $out_dir/glm/rh.glm.glmdir_nfl \
--eres-save
#run with clusterwise corrections for negative correlations for nfl
echo "Running mri_glmfit-sim for left hemisphere for nfl"
mri_glmfit-sim \
--glmdir $out_dir/glm/lh.glm.glmdir_nfl \
--perm 1000 4.0 neg \
--cwp 0.05 \
--2spaces \
--bg 1
echo "Running mri_glmfit-sim for right hemisphere for nfl"
mri_glmfit-sim \
--glmdir $out_dir/glm/rh.glm.glmdir_nfl \
--perm 1000 4.0 neg \
--cwp 0.05 \
--2spaces \
--bg 1

#run mri_glm_fit for ab4240_ratio
echo "Running mri_glm_fit for left hemisphere for ab4240_ratio"
mri_glmfit \
--y $out_dir/all.lh.mgx.ctx.fsaverage.sm05.nii.gz \
--fsgd $fsgd_file_ab4240_ratio \
--C $matrix_file \
--surf fsaverage lh \
--cortex \
--glmdir $out_dir/glm/lh.glm.glmdir_ab4240_ratio \
--eres-save
echo "Running mri_glm_fit for right hemisphere for ab4240_ratio"
mri_glmfit \
--y $out_dir/all.rh.mgx.ctx.fsaverage.sm05.nii.gz \
--fsgd $fsgd_file_ab4240_ratio \
--C $matrix_file \
--surf fsaverage rh \
--cortex \
--glmdir $out_dir/glm/rh.glm.glmdir_ab4240_ratio \
--eres-save
#run with clusterwise corrections for negative correlations for ab4240_ratio
echo "Running mri_glmfit-sim for left hemisphere for ab4240_ratio"
mri_glmfit-sim \
--glmdir $out_dir/glm/lh.glm.glmdir_ab4240_ratio \
--perm 1000 4.0 pos \
--cwp 0.05 \
--2spaces \
--bg 1
echo "Running mri_glmfit-sim for right hemisphere for ab4240_ratio"
mri_glmfit-sim \
--glmdir $out_dir/glm/rh.glm.glmdir_ab4240_ratio \
--perm 1000 4.0 pos \
--cwp 0.05 \
--2spaces \
--bg 1

#run mri_glm_fit for tau
echo "Running mri_glm_fit for left hemisphere for tau"
mri_glmfit \
--y $out_dir/all.lh.mgx.ctx.fsaverage.sm05.nii.gz \
--fsgd $fsgd_file_tau \
--C $matrix_file \
--surf fsaverage lh \
--cortex \
--glmdir $out_dir/glm/lh.glm.glmdir_tau \
--eres-save
echo "Running mri_glm_fit for right hemisphere for tau"
mri_glmfit \
--y $out_dir/all.rh.mgx.ctx.fsaverage.sm05.nii.gz \
--fsgd $fsgd_file_tau \
--C $matrix_file \
--surf fsaverage rh \
--cortex \
--glmdir $out_dir/glm/rh.glm.glmdir_tau \
--eres-save
#run with clusterwise corrections for negative correlations for tau
echo "Running mri_glmfit-sim for left hemisphere for tau"
mri_glmfit-sim \
--glmdir $out_dir/glm/lh.glm.glmdir_tau \
--perm 1000 4.0 neg \
--cwp 0.05 \
--2spaces \
--bg 1
echo "Running mri_glmfit-sim for right hemisphere for tau"
mri_glmfit-sim \
--glmdir $out_dir/glm/rh.glm.glmdir_tau \
--perm 1000 4.0 neg \
--cwp 0.05 \
--2spaces \
--bg 1


