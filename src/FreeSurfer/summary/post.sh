set -x

cd /OUTPUTS/SUBJECTS

for i in *;do
    cd /OUTPUTS/SUBJECTS/$i/surf
    echo "-viewsize 400 400 --layout 1 --viewport 3d --hide-3d-slices" > commands.txt
    echo "-f lh.inflated:overlay=lh.thickness:overlay_threshold=0.1,3" >> commands.txt
    echo "-ss lh_lat_thick.png -noquit" >> commands.txt
    echo "-cam azimuth 180" >> commands.txt
    echo "-ss lh_med_thick.png -noquit" >> commands.txt
    echo "--hide surface" >> commands.txt
    echo "-f rh.inflated:overlay=rh.thickness:overlay_threshold=0.1,3" >> commands.txt
    echo "-ss rh_lat_thick.png -noquit" >> commands.txt
    echo "-cam azimuth 180" >> commands.txt
    echo "-ss rh_med_thick.png -noquit" >> commands.txt
    echo "--hide surface" >> commands.txt
    echo "-f lh.inflated:annot=aparc" >> commands.txt
    echo "-ss lh_lat_s100i.png -noquit" >> commands.txt
    echo "-cam azimuth 180" >> commands.txt
    echo "-ss lh_med_s100i.png -noquit" >> commands.txt
    echo "--hide surface" >> commands.txt
    echo "-f rh.inflated:annot=aparc" >> commands.txt
    echo "-ss rh_lat_s100i.png -noquit" >> commands.txt
    echo "-cam azimuth 180" >> commands.txt
    echo "-ss rh_med_s100i.png -noquit" >> commands.txt
    echo "--hide surface" >> commands.txt
    echo "-f lh.pial:annot=aparc" >> commands.txt
    echo "-ss lh_lat_s100.png -noquit" >> commands.txt
    echo "-cam azimuth 180" >> commands.txt
    echo "-ss lh_med_s100.png -noquit" >> commands.txt
    echo "--hide surface" >> commands.txt
    echo "-f rh.pial:annot=aparc" >> commands.txt
    echo "-ss rh_lat_s100.png -noquit" >> commands.txt
    echo "-cam azimuth 180" >> commands.txt
    echo "-ss rh_med_s100.png -noquit" >> commands.txt
    echo "-quit" >> commands.txt

    xvfb-run -a --server-args "-screen 0 1920x1080x24" freeview -cmd commands.txt
    
    for p in [lr]h_*.png; do 
        mogrify -fuzz 1% -trim +repage -resize 400x400 $p
    done

    montage -mode concatenate -quality 100 -pointsize 36 -tile 4x \
    -background black -fill white -gravity center +repage -crop 400x400+0+0 \
    -extent 400x400 -border 20 -bordercolor black -resize 400x400 -title "SUBJECT: $i" \
    lh_lat_s100.png lh_med_s100.png rh_med_s100.png rh_lat_s100.png \
    lh_lat_s100i.png lh_med_s100i.png rh_med_s100i.png rh_lat_s100i.png \
    lh_lat_thick.png lh_med_thick.png rh_med_thick.png rh_lat_thick.png \
    montage-$i.png
done

convert /OUTPUTS/SUBJECTS/*/surf/montage*.png -bordercolor white -border 100x500 -page letter /OUTPUTS/report.pdf

# Delete subject directories so they don't get uploaded
rm -r /OUTPUTS/SUBJECTS
