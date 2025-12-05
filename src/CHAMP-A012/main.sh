#!/bin/bash


in_dir='/INPUTS'
out_dir='/OUTPUTS/DATA'


#cp fsaverage to inputs
cp -r /usr/local/freesurfer/subjects/fsaverage $in_dir


echo -n "" > $out_dir/subjects.txt

# for each subject sample mgx vol to left and right hemisphere

for subject in $in_dir/*; do
    echo $subject
    #skip if subject is not a directory
    if [ ! -d $subject ]; then
        continue
    fi

    #skip if subject is fsaverage
    if [ $subject == "$in_dir/fsaverage" ]; then
        continue
    fi

    subject_id=$(basename $subject)


    sub_feobv=$in_dir/$subject_id/assessors/*/*FEOBVQA_v4*/SUBJ/gtmpvc.esupravwm.output

    sub_surf_w_input=$in_dir/$subject_id/assessors/*/*FEOBVQA_v4*/SUBJ

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

    echo $subject_id >> $our_dir/subjects.txt

    mkdir -p $out_dir/$subject_id

    for h in lh rh;do
    
        echo $subject_id $h

        # Map SUVR volume to fsaverage surface, projected to middle of cortex
        mri_vol2surf \
        --mov $sub_feobv/mgx.ctxgm.nii.gz \
        --reg $sub_feobv/aux/bbpet2anat.lta \
        --hemi $h \
        --projfrac 0.5 \
        --o $out_dir/$subject_id/$h.mgx.ctx.fsaverage.sm00.nii.gz \
        --cortex \
        --trgsubject fsaverage \
        --srcsubject $sub_surf \
        --sd $in_dir

        # Calculate per parcel stats
        for p in 100 200 400;do
            mri_segstats \
            --annot fsaverage $h Schaefer2018_${p}Parcels_7Networks_order \
            --in $out_dir/$subject_id/$h.mgx.ctx.fsaverage.sm00.nii.gz \
            --sum $out_dir/$subject_id/$h.Schaefer2018_${p}Parcels_7Networks_order.stats.txt \
            --sd $in_dir
        done

        # Also Yeo7/17 whole network parcels
        for y in 7 17;do
            mri_segstats \
                --annot fsaverage $h Yeo2011_${y}Networks_N1000 \
                --in $out_dir/$subject_id/$h.mgx.ctx.fsaverage.sm00.nii.gz \
                --sum $out_dir/$subject_id/$h.Yeo2011_${y}Networks.stats.txt \
                --sd $in_dir
        done
    done
done
