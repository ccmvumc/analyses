set -x

mkdir -p /OUTPUTS/SUBJECTS

cd /INPUTS

for i in *;do

    cd /INPUTS/$i

    for j in *;do

        # Copy from inputs to outputs
        cp -r /INPUTS/$i/$j/assessors/* /OUTPUTS/SUBJECTS/${j}

        # Append to subject list
        echo ${j} >> /OUTPUTS/subjects.txt

    done
done
