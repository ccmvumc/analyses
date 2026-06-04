# TODO: Make template with mri_robust_template
set -x
    
cd /INPUTS

for i in *;do
    echo $i

    mkdir -p /OUTPUTS/SUBJECTS/$i

    cd /OUTPUTS/SUBJECTS/$i

    cp /INPUTS/$i/gtmpvc.esupravwm.output/gtm.stats.dat .

    # Make file per column
    yes $i | head -n 100 > subject.txt
    yes esupravwm | head -n 100 > ref.txt
    yes gtm | head -n 100 > gtm.txt
    awk '{print $3}' gtm.stats.dat > labels.txt
    awk '{print $7}' gtm.stats.dat > gtm.suvr

    # Combine into single file
    paste subject.txt ref.txt gtm.txt labels.txt gtm.suvr >> all.suvr

done

cat /OUTPUTS/SUBJECTS/*/all.suvr > /OUTPUTS/suvr.txt
