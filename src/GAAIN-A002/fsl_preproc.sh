#!/bin/bash

# Initialize FSL
source /Users/jasonrussell/fsl/etc/fslconf/fsl.sh

# Directory containing all subjects
input_dir="/Users/jasonrussell/Documents/INPUTS/gaain_A002/scans"
output_dir="/Users/jasonrussell/Documents/OUTPUTS/gaain_A002"

# Ensure output directory exists
mkdir -p "$output_dir"

# Loop through each subject folder in the input directory
for subject_dir in "$input_dir"/*; do
  # Extract subject ID from the path
  subject_id=$(basename "$subject_dir")
  
  # Find the PET image in the current subject's directory
  pet_image=$(find "$subject_dir/PET" -name "*Brain_Dynamic.nii.gz" | head -n 1)
  
  # Skip if no PET image is found
  if [ -z "$pet_image" ]; then
    echo "No PET image found for subject: $subject_id, skipping..."
    continue
  fi
  
  echo "Processing PET image for subject: $subject_id"
  
  # Define directories for intermediate and output files
  subject_output_dir="$output_dir/$subject_id"
  
  #MCFLIRT images
  mcflirt_out="$subject_output_dir/pet_mcf.nii.gz"
  mcflirt -in "$pet_image" -out "$mcflirt_out" -stages 4 -mats -plots
  
  # Calculate the mean of the volumes
  mean_image="$subject_output_dir/mean_pet.nii.gz"
  fslmaths "$mcflirt_out" -Tmean "$mean_image"
  
  echo "Mean PET image saved for subject $subject_id at: $mean_image"
done

echo "Processing complete for all subjects."
