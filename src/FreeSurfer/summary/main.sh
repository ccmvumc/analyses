export SUBJECTS_DIR=/OUTPUTS/DATA/SUBJECTS

cp -r /usr/local/freesurfer/subjects/fsaverage $SUBJECTS_DIR

cd $SUBJECTS_DIR

# Write stats table for each hemisphere for thickness, volume
aparcstats2table --skip --delimiter comma --subjectsfile /OUTPUTS/subjects.txt --hemi lh --meas thickness --tablefile /OUTPUTS/DATA/aparc.lh.thickness.csv
aparcstats2table --skip --delimiter comma --subjectsfile /OUTPUTS/subjects.txt --hemi rh --meas thickness --tablefile /OUTPUTS/DATA/aparc.rh.thickness.csv
aparcstats2table --skip --delimiter comma --subjectsfile /OUTPUTS/subjects.txt --hemi lh --meas volume --tablefile /OUTPUTS/DATA/aparc.lh.volume.csv
aparcstats2table --skip --delimiter comma --subjectsfile /OUTPUTS/subjects.txt --hemi rh --meas volume --tablefile /OUTPUTS/DATA/aparc.rh.volume.csv

# Volume stats
asegstats2table --skip --delimiter comma --subjectsfile /OUTPUTS/subjects.txt --meas volume --tablefile /OUTPUTS/DATA/aseg.volume.csv

echo DONE
