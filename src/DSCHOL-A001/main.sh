#!/bin/bash

python /Users/jasonrussell/Documents/code/analyses_local/src/DSCHOL-A001/normalize.py
python /Users/jasonrussell/Documents/code/analyses_local/src/DSCHOL-A001/indiv_masks.py
python /Users/jasonrussell/Documents/code/analyses_local/src/DSCHOL-A001/study_specific_gm_mask.py
python /Users/jasonrussell/Documents/code/analyses_local/src/DSCHOL-A001/voxelwise_centiloid_glm.py
