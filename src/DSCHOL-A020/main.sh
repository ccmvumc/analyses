export SUBJECTS_DIR=/OUTPUTS/DATA/SUBJECTS

cd $SUBJECTS_DIR

# Write stats table for each hemisphere for thickness, volume
aparcstats2table --skip --delimiter comma --subjectsfile /OUTPUTS/subjects.txt --hemi lh --meas volume --tablefile /OUTPUTS/DATA/aparc.lh.volume.csv
aparcstats2table --skip --delimiter comma --subjectsfile /OUTPUTS/subjects.txt --hemi rh --meas volume --tablefile /OUTPUTS/DATA/aparc.rh.volume.csv

# Volume stats
asegstats2table --skip --delimiter comma --subjectsfile /OUTPUTS/subjects.txt --meas volume --tablefile /OUTPUTS/DATA/aseg.volume.csv

echo DONE


#mri_segstats --seg <segvol> --annot <subject hemi parc> --slabel <subject hemi label> --sum <file>

#asegstats2table --subjects sub-101 sub-103 --common-segs --meas volume --stats=aseg.stats --table=segstats.txt

#ROI=(supravwm supravwm_eroded cortwm_eroded antflobe latplobe lattlobe antcing postcing compositegm cortwm cblmgm cblmwm)
#for r in "${ROI[@]}"
#do
#    echo -n $r >> $TXT
#    mri_segstats --seg ROI_${r}.nii.gz --i PET_mcf_meanvol.nii.gz --id 1 --sum ${r}_stats.txt
#    grep Seg0001 ${r}_stats.txt | awk '{print ","$8","$9","$6","$7","$4}' >> $TXT
#done
