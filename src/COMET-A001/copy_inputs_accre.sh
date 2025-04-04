#!/usr/bin/env bash
#
# Copy input files to the output/working directory so we don't mess them up. We
# generally assume the output directory starts out empty and will not be 
# interfered with by any other processes - certainly this is true for XNAT/DAX.

echo Running $(basename "${BASH_SOURCE}"), out_dir equals "${out_dir}" 

mkdir -p "${out_dir}"/statistics
mkdir "${out_dir}"/WAVELET_OUTPUT_DIR
cp -r "/INPUTS/." "${out_dir}"/WAVELET_OUTPUT_DIR
rm -r "${out_dir}"/WAVELET_OUTPUT_DIR/xvfb*



