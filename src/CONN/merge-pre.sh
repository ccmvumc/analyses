# convert covars to mat file for CONN
if [ -f "/INPUTS/covariates.csv" ]; then
	python /REPO/src/CONN/covariate_csv2mat.py

	# Create the contrasts file
	python /REPO/src/CONN/make_contrasts.py
else
	echo "File not found /INPUTS/covariates.csv"
fi
