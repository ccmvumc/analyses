# copy to outputs, unzip the conn projects
cd /INPUTS
for i in */;do
	echo $i
	mkdir /OUTPUTS/$i
	unzip /INPUTS/${i}assessors/*/*/CONN/conn_project.zip -d /OUTPUTS/${i}
	cp /INPUTS/${i}assessors/*/*/CONN/conn_project.mat /OUTPUTS/${i}
done

# Make mat files for covariates and contrasts
if [ -f "/INPUTS/covariates.csv" ]; then
	# convert covars to mat file for CONN
	python /REPO/src/CONN/covariate_csv2mat.py

	# Create the contrasts file
	python /REPO/src/CONN/make_contrasts.py
else
	echo "File not found /INPUTS/covariates.csv"
fi
