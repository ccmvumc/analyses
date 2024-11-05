#!/bin/bash

# Directory containing all subjects
input_dir="/Users/jasonrussell/Documents/INPUTS/gaain_A003/scans"
output_dir="/Users/jasonrussell/Documents/OUTPUTS/gaain_A003"

# Ensure output directory exists
mkdir -p "$output_dir"

# Loop through each subject folder in the input directory
for subject_dir in "$input_dir"/*; do
  # Extract subject ID from the path
  subject_id=$(basename "$subject_dir")
  
  # Find the images in the current subject's directory
  pib_image=$(find "$subject_dir/PET_pib/DICOM" | head -n 1)
  
  # Skip if no PET image is found
  if [ -z "$pib_image" ]; then
    echo "No PiB image found for subject: $subject_id, skipping..."
    continue
  fi

  
  echo "Converting PiB DICOM images for subject: $subject_id"
  
  # Define directories for intermediate and output files
  subject_output_dir="$output_dir/$subject_id"
  pib_dir="$subject_output_dir/pib"
  mkdir -p "$pib_dir"
  
  # Convert pib dicoms
  dcm2niix -o "$pib_dir" -f "${subject_id}_pib" "$pib_image"
  
  
  echo "Nifti PiB image saved for subject $subject_id at: $pib_dir"
done

  
for subject_dir in "$input_dir"/*; do
  # Extract subject ID from the path
  subject_id=$(basename "$subject_dir")
  
  # Find the images in the current subject's directory
  mr_images=$(find "$subject_dir/MR/DICOM" | head -n 1)
  
  # Skip if no PET image is found
  if [ -z "$mr_images" ]; then
    echo "No MR image found for subject: $subject_id, skipping..."
    continue
  fi
  
  echo "Converting MR DICOM images for subject: $subject_id"
  
  # Define directories for intermediate and output files
  subject_output_dir="$output_dir/$subject_id"
  mr_dir="$subject_output_dir/mr"
  mkdir -p "$mr_dir"
  
  # Convert pib dicoms
  dcm2niix -o "$mr_dir" -f "${subject_id}_mr" "$mr_images"
  
  
  echo "Nifti PiB image saved for subject $subject_id at: $mr_images"
done

for subject_dir in "$input_dir"/*; do
  # Extract subject ID from the path
  subject_id=$(basename "$subject_dir")
  
  # Find the images in the current subject's directory
  petav45_images=$(find "$subject_dir/PET_amyvid/DICOM" | head -n 1)
  
  # Skip if no PET image is found
  if [ -z "$petav45_images" ]; then
    echo "No Amyvid image found for subject: $subject_id, skipping..."
    continue
  fi
  
  echo "Converting AV45 DICOM images for subject: $subject_id"
  
  # Define directories for intermediate and output files
  subject_output_dir="$output_dir/$subject_id"
  av45_dir="$subject_output_dir/av45"
  mkdir -p "$av45_dir"
  
  # Convert pib dicoms
  dcm2niix -o "$av45_dir" -f "${subject_id}_av45" "$petav45_images"
  
  
  echo "Nifti PiB image saved for subject $subject_id at: $petav45_images"
done

echo "Conversion from DICOM to Nifti complete for all subjects."
