#!/usr/bin/env bash
#
# Primary entrypoint for our pipeline. This just parses the command line 
# arguments, exporting them in environment variables for easy access
# by other shell scripts later. Then it calls the rest of the pipeline.
#
# Example usage:
# 
# pipeline_entrypoint.sh --image_niigz /path/to/image.nii.gz --diameter_mm 30

# This statement at the top of every bash script is helpful for debugging
echo Running $(basename "${BASH_SOURCE}")

# Initialize defaults for any input parameters where that seems useful
export times=-704:4:1500
export bins=80
export freqrange_low=2
export freqrange_high=30
export thrsh=.05
export out_dir=/OUTPUTS

# Parse input options
while [[ $# -gt 0 ]]
do
    key="$1"
    case $key in 
        
        --times)
            # times for trials in ms, must match trial size unless wavelt function code is changed, e.g., times = 0:4:2000
            export times="$2"; shift; shift ;;

        --bins)
            # number of bins to test e.g., 80
            export bins="$2"; shift; shift ;;

        --freqrange_low)
            # array containing lower and upper bounds of frequency space to sample (e.g. [2,30])
            export freqrange_low="$2"; shift; shift ;;
            
        --freqrange_high)
            # array containing lower and upper bounds of frequency space to sample (e.g. [2,30])
            export freqrange_high="$2"; shift; shift ;;
            
         --thrsh)
            # clust threshold
            export thrsh="$2"; shift; shift ;;

        --out_dir)
            # where outputs stored, also working directory
            export out_dir="$2"; shift; shift ;;

        *)
            echo "Input ${1} not recognized"
            shift ;;

    esac
done


# Now that we have all the inputs stored in environment variables, call the
# main pipeline. We run it in xvfb so that we have a virtual display available.
xvfb-run -n $(($$ + 99)) -s '-screen 0 1600x1200x24 -ac +extension GLX' \
    bash pipeline_main.sh
