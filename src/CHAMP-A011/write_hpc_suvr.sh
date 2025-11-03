#!/bin/bash

in_dir='/INPUTS'
out_dir='/OUTPUTS/DATA'

#generate biolateral HPC
for subject in $in_dir/*; do
    #get subject name
    subject_name=$(basename $subject)
    mkdir -p $out_dir/$subject_name
    mri_binarize \
        --i $subject/assessors/*/*FEOBVQA_v4*/SUBJ/mri/gtmseg.mgz \
        --o $out_dir/$subject_name/bilat_hpc.nii.gz \
        --match 17 53   
done

#calulate SUVRS in hippocampus and L/R HPC separately
for subject in $in_dir/*; do
    subject_name=$(basename $subject)
    mkdir -p $out_dir/$subject_name
    mri_segstats --seg "${out_dir}/${subject_name}/bilat_hpc.nii.gz" --id 1 --i "${subject}/assessors/*/*FEOBVQA_v4*/SUBJ/mri/gtmpvc.output/rbv.nii.gz" --avgwf "${out_dir}/${subject_name}/full_hpc.txt"
    mri_segstats --seg "${subject}/assessors/*/*FEOBVQA_v4*/SUBJ/mri/gtmseg.mgz" --id 17 --i "${subject}/assessors/*/*FEOBVQA_v4*/SUBJ/mri/gtmpvc.output/rbv.nii.gz" --avgwf "${out_dir}/${subject_name}/Left_hpc.txt"
    mri_segstats --seg "${subject}/assessors/*/*FEOBVQA_v4*/SUBJ/mri/gtmseg.mgz" --id 53 --i "${subject}/assessors/*/*FEOBVQA_v4*/SUBJ/mri/gtmpvc.output/rbv.nii.gz" --avgwf "${out_dir}/${subject_name}/Right_hpc.txt"
done

#combine all .txts into one csv
echo "Subject,Full_HPC_SUVR,Left_HPC_SUVR,Right_HPC_SUVR" > $out_dir/hpc_suvr_summary.csv
for subject in $in_dir/*; do
    subject_name=$(basename $subject)
    full_hpc_suvr=$(cat "${out_dir}/${subject_name}/full_hpc.txt")
    left_hpc_suvr=$(cat "${out_dir}/${subject_name}/Left_hpc.txt")
    right_hpc_suvr=$(cat "${out_dir}/${subject_name}/Right_hpc.txt")
    echo "${subject_name},${full_hpc_suvr},${left_hpc_suvr},${right_hpc_suvr}" >> $out_dir/hpc_suvr_summary.csv
done    