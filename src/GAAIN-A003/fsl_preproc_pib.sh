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
  pib_image="$subject_dir/pib/${subject_id}_pib.nii"
  piba_image="$subject_dir/pib/${subject_id}_piba.nii"
  pibb_image="$subject_dir/pib/${subject_id}_pibb.nii"
  pibc_image="$subject_dir/pib/${subject_id}_pibc.nii"

  # Define the output mean image path
  subject_output_dir="$subject_dir/pib"
  mean_image="$subject_output_dir/mean_pet_pib.nii.gz"
  
  # Check if the main PIB image exists
  if [ -f "$pib_image" ]; then
    dim4=$(fslinfo "$pib_image" | grep '^dim4' | awk '{print $2}')

    if [ -f "$pibb_image" ]; then
      # All four images exist; calculate the mean
      echo "Calculating mean of ${subject_id}_pib images"
      fslmaths "$pib_image" -add "$piba_image" -add "$pibb_image" -add "$pibc_image" -div 4 "$mean_image"

    elif [ -f "$piba_image" ]; then
      # Two images exist; calculate the mean of two
      echo "Calculating mean of ${subject_id}_pib two images"
      fslmaths "$pib_image" -add "$piba_image" -div 2 "$mean_image"

    elif [ "$dim4" -eq 4 ]; then
      # Single image with 4 frames; calculate temporal mean
      echo "Only ${subject_id}_pib.nii found for subject: $subject_id. Image has ${dim4} frames."
      fslmaths "$pib_image" -Tmean "$mean_image"

    elif [ "$dim4" -eq 1 ]; then
      # Single image with 1 frame; copy directly
      echo "Only ${subject_id}_pib.nii found for subject: $subject_id. Saving it directly as the mean image."
      cp "$pib_image" "$mean_image"

    elif [ "$dim4" -gt 4 ] || [ "$dim4" -eq 2 ] || [ "$dim4" -eq 3 ]; then
      # Unexpected number of frames
      echo "ERROR: UNEXPECTED NUMBER OF FRAMES. ${dim4} frames."

    fi

    echo "Mean pib PET image saved for subject $subject_id at: $mean_image"

  else
    # No PIB images found; skip this subject
    echo "No PIB PET image found for subject: $subject_id, skipping..."
    continue
  fi
done

echo "Processing complete for all subjects."
