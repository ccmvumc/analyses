#!/bin/bash

# Initialize FSL
source /Users/jasonrussell/fsl/etc/fslconf/fsl.sh

# Directory containing all subjects
input_dir="/Users/jasonrussell/Documents/OUTPUTS/gaain_A003"
output_dir="/Users/jasonrussell/Documents/OUTPUTS/gaain_A003"

# Loop through each subject folder in the input directory
for subject_dir in "$input_dir"/*; do
  # Extract subject ID from the path
  subject_id=$(basename "$subject_dir")
  
  # Define the PET images paths
  av45_image="$subject_dir/av45/${subject_id}_av45.nii"
  av45a_image="$subject_dir/av45/${subject_id}_av45a.nii"
  
  # Define the output mean image path
  subject_output_dir="$output_dir/$subject_id/av45"
  mkdir -p "$subject_output_dir"
  mean_image="$subject_output_dir/mean_pet_av45.nii.gz"
  
  # Check if the main av45 image exists
  if [ -f "$av45_image" ]; then
    dim4=$(fslinfo "$av45_image" | grep '^dim4' | awk '{print $2}')

    if [ -f "$av45a_image" ]; then
      # Both images exist; calculate the mean
      echo "Calculating mean of ${subject_id}_av45.nii and ${subject_id}_av45a.nii for subject: $subject_id"
      fslmaths "$av45_image" -add "$av45a_image" -div 2 "$mean_image"
      echo "Mean av45 PET image saved for subject $subject_id at: $mean_image"

    elif [ "$dim4" -eq 2 ]; then
      # Only av45 image exists and has 2 frames; calculate temporal mean
      echo "Only ${subject_id}_av45.nii found for subject: $subject_id. Image has ${dim4} frames."
      fslmaths "$av45_image" -Tmean "$mean_image"
      echo "Mean av45 PET image saved for subject $subject_id at: $mean_image"

    elif [ "$dim4" -eq 1 ]; then
      # Single frame; copy it as mean image
      cp "$av45_image" "$mean_image"
      echo "Mean av45 PET image saved for subject $subject_id at: $mean_image"

    elif [ "$dim4" -gt 2 ]; then
      # Unexpected number of frames
      echo "ERROR: UNEXPECTED NUMBER OF FRAMES. ${dim4} frames."

    fi
  else
    # No av45 images found; skip this subject
    echo "No av45 PET image found for subject: $subject_id, skipping..."
    continue
  fi
done

echo "Processing complete for all subjects."
