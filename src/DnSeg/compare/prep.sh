set -x

mkdir -p /OUTPUTS/SUBJECTS

cd /INPUTS

for i in *; do 
    if [ ! -d "/INPUTS/$i" ]; then
        continue
    fi

    cd /INPUTS/${i}

    for j in *; do
         if [ ! -d "/INPUTS/$i/$j" ]; then
            continue
        fi

        echo "$i/$j"

        mkdir -p /OUTPUTS/SUBJECTS/$j

        cp -r /INPUTS/$i/$j/assessors/*/* /OUTPUTS/SUBJECTS/$j

    done
done
