# copy to outputs, unzip the conn projects
cd /INPUTS
for i in */;do
	echo $i
	mkdir /OUTPUTS/$i
	unzip /INPUTS/${i}assessors/*/*/CONN/conn_project.zip -d /OUTPUTS/${i}
	cp /INPUTS/${i}assessors/*/*/CONN/conn_project.mat /OUTPUTS/${i}
done


# merge
echo "Merging CONN projects"
xvfb-run \
-e /OUTPUTS/xvfb.err -f /OUTPUTS/xvfb.auth \
-a --server-args "-screen 0 1600x1200x24" \
/opt/conn/run_conn.sh \
/opt/mcr/v912 batch \
/REPO/src/CONN/merge.m


# Delete individual subjects to prevent uploading
cd /INPUTS
for i in */;do
	echo $i
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
else
	echo "File not found /OUTPUTS/covariates.mat"
fi


echo "ALL DONE!"
