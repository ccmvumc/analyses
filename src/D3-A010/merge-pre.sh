python -u /REPO/src/CONN/prep.py

# Make mat files for covariates and contrasts
if [ -f "/INPUTS/covariates.csv" ]; then
	# convert covars to mat file for CONN
	python -u /REPO/src/CONN/covariate_csv2mat.py

	# Create the contrasts file
	python -u /REPO/src/D3-A010/make_contrasts.py
else
	echo "File not found /INPUTS/covariates.csv"
fi
