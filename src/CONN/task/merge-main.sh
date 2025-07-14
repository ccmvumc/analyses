# merge
echo "Merging CONN projects"
xvfb-run \
-e /OUTPUTS/xvfb.err -f /OUTPUTS/xvfb.auth \
-a --server-args "-screen 0 1600x1200x24" \
/opt/conn/run_conn.sh \
/opt/mcr/v912 batch \
/REPO/src/CONN/merge.m

rm /OUTPUTS/xvfb.*

# Delete individual subjects to prevent uploading
cd /INPUTS
for i in */;do
	echo $i

    # Append to subject list (removing last character slash)
    echo ${i%?} >> /OUTPUTS/subjects.txt

	rm -r /OUTPUTS/${i}
done

echo "ALL DONE!"
