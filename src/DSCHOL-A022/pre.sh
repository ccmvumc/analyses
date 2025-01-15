set -x

mkdir -p /OUTPUTS/DATA/SUBJECTS

cd /INPUTS

for i in *;do

    cd /INPUTS/$i

    # Copy from inputs to outputs
    cp -r /INPUTS/$i/assessors/* /OUTPUTS/DATA/SUBJECTS/${i}

    # Append to subject list
    echo ${i} >> /OUTPUTS/subjects.txt

done
