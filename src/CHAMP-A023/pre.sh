set -x

# Make the subjects folder
mkdir -p /OUTPUTS/SUBJECTS

cd /INPUTS

ls -ltrR

# Copy subjects to outputs
for i in */;do
    echo $i

    cp -r /INPUTS/$i/assessors/* /OUTPUTS/DATA/SUBJECTS/${i}

    # Append to subject list
    echo ${i} >> /OUTPUTS/subjects.txt
done
