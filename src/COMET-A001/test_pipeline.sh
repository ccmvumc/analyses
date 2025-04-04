#!/usr/bin/env bash
#
# Test the pipeline outside the container. Be sure the src directory is in the
# path.

# Just the PDF creation part
# export label_info="TEST LABEL"
# export out_dir=../OUTPUTS
# make_pdf.sh
# exit 0

# The entire thing
pipeline_entrypoint.sh \
    --cov1 '[1 2 3 4 5 1 2 3 4 5 1 2 3 4]' \
    --cov2 '[1 2 3 4 5 1 2 3 4 5 1 2 3 4]'
