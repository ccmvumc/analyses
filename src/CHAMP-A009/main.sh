#!/bin/bash

#run gen_fsdg.py
python /REPO/src/CHAMP-A009/gen_fsdg.py
echo "Generated fsgd file"

#run surfacebased.sh
bash /REPO/src/CHAMP-A009/surfacebased.sh
echo "Fini!"