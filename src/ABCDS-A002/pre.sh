mkdir /OUTPUTS/SUBJECTS

cd /INPUTS

for i in *;do echo $i;cp -r  $i/*/*/*/*/e1.long.LONG /OUTPUTS/SUBJECTS/${i}_e1.long.${i};done
for i in *;do echo $i;cp -r  $i/*/*/*/*/e2.long.LONG /OUTPUTS/SUBJECTS/${i}_e2.long.${i};done
for i in *;do echo $i;cp -r  $i/*/*/*/*/e3.long.LONG /OUTPUTS/SUBJECTS/${i}_e3.long.${i};done
for i in *;do echo $i;cp -r  $i/*/*/*/*/e5.long.LONG /OUTPUTS/SUBJECTS/${i}_e5.long.${i};done

# Make list of subjects
cd /OUTPUTS/SUBJECTS

for i in *;do
    echo $i >> /OUTPUTS/subjects.txt
done
