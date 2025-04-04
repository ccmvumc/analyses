#!/usr/bin/env bash
#
# Main pipeline. We'll call the matlab part from here. The benefit of wrapping
# everything in a shell script like this is that we can more easily use shell
# commands to move files around, use FSL for some pre- or post-processing, and 
# use fsleyes after the matlab has finished to create a QA PDF.

echo Running $(basename "${BASH_SOURCE}")

# Copy inputs to the working directory
copy_inputs_accre.sh

# Shell script based preprocessing


# Then the matlab. It is written so that we must pass the inputs as command
# line arguments, although we could use matlab's getenv to pull them from the
# environment instead if desired.

run_matlab_entrypoint.sh "${MATLAB_RUNTIME}" \
   times "${times}" \
   bins "${bins}" \
   freqrange_low "${freqrange_low}" \
   freqrange_high "${freqrange_high}" \
   thrsh "${thrsh}"
#finalize/ remove inputs
#finalize.sh
