#!/usr/bin/env bash
#
# Use fsleyes to create a PDF QA report. This is entirely fidgety, but still
# is easier than doing it in Matlab.

echo Running $(basename "${BASH_SOURCE}")

# Work in output directory
cd ${out_dir}/2ndlvl

# Binarize the segmentation and find its center of mass, as a starting point for
# slice placement in the visualization
# fslmaths seg -bin mask

#find center of .05 thresholded p-stat image
com=$(fslstats spmTHRP_0001 -c)
XYZ=(${com// / })

# Create an axial view of T1 with ROI overlay for a series of axial slices. 
# Offsets are specified in mm from the computed center of mass of the brain.
#for sl in -040 -030 -020 -010 000 010 020 030 040 050 060; do
#
#    Z=$(echo "${XYZ[2]} + ${sl}" | bc -l)
#    echo "    Slice ${sl} at ${XYZ[0]} ${XYZ[1]} ${Z}"
#
#    fsleyes render -of slice_${sl}.png \
#        --scene ortho --worldLoc ${XYZ[0]} ${XYZ[1]} ${Z} \
#        --layout horizontal --hideCursor --hideLabels --hidex --hidey \
#        holed_t1 --overlayType volume \
#        holed_seg --overlayType label --lut random_big --outline --outlineWidth 2
#
#done

## patrick is using this loop
for sl in -040 -030 -020 -010 000 010 020 030 040 050 060; do

    Z=$(echo "${XYZ[2]} + ${sl}" | bc -l)
    echo "    Slice ${sl} at ${XYZ[0]} ${XYZ[1]} ${Z}"

    fsleyes render -of slice_${sl}.png \
        --scene ortho --worldLoc ${XYZ[0]} ${XYZ[1]} ${Z} \
        --layout horizontal --hideCursor --hidex --hidey \
	/opt/MNI152_T1_1mm --overlayType volume \
	spmTHRP_0001 --cmap hot	

done




# Combine into single image using ImageMagick. Pretty hacky way of getting the
# slices in the right order, but it works
montage -mode concatenate slice_-0{4,3,2,1}*.png slice_0*.png \
    -tile 3x4 -quality 100 -background black -gravity center \
    -border 20 -bordercolor black page1.png

# Resize and add text annotations. We choose a large but not ridiculous
# pixel size for the full page.
convert \
    -size 2600x3365 xc:white \
    -gravity center \( page1.png -resize 2400x \) -composite \
    -gravity North -pointsize 48 -annotate +0+100 \
    "pos effect con" \
    -gravity SouthEast -pointsize 48 -annotate +100+100 "$(date)" \
    -gravity NorthWest -pointsize 48 -annotate +100+200 "${label_info}" \
    page1.png

# Convert to PDF
convert page1.png QA.pdf

# Clean up
rm page1.png slice_*.png

# move QA image to QA folder to stor in XNAT resources 
mv "${out_dir}/2ndlvl/QA.pdf" "${out_dir}/QA"

