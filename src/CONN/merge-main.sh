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

    # Append to subject list    
    echo ${j} >> /OUTPUTS/subjects.txt

	rm -r /OUTPUTS/${i}
done


# covars
if [ -f "/OUTPUTS/covariates.mat" ]; then
	echo "Loading covariates to CONN project"
	xvfb-run \
	-e /OUTPUTS/xvfb.err -f /OUTPUTS/xvfb.auth \
	-a --server-args "-screen 0 1600x1200x24" \
	/opt/conn/run_conn.sh \
	/opt/mcr/v912 batch \
	/REPO/src/CONN/load_covariates.m

	rm /OUTPUTS/xvfb.*

	# Run the results
	echo "Running 2nd level contrasts in CONN"
	xvfb-run \
	-e /OUTPUTS/xvfb.err -f /OUTPUTS/xvfb.auth \
	-a --server-args "-screen 0 1600x1200x24" \
	/opt/conn/run_conn.sh \
	/opt/mcr/v912 batch \
	/REPO/src/CONN/second_level.m

	rm /OUTPUTS/xvfb.*

else
	echo "File not found /OUTPUTS/covariates.mat"
fi


echo "ALL DONE!"
