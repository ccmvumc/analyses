mkdir /OUTPUTS/SUBJECTS

cd /INPUTS

for i in *;do echo $i;cp -r  $i/*/*/*/*/e1.long.LONG /OUTPUTS/SUBJECTS/${i}_e1.long.${i};done
for i in *;do echo $i;cp -r  $i/*/*/*/*/e2.long.LONG /OUTPUTS/SUBJECTS/${i}_e2.long.${i};done
for i in *;do echo $i;cp -r  $i/*/*/*/*/e3.long.LONG /OUTPUTS/SUBJECTS/${i}_e3.long.${i};done
