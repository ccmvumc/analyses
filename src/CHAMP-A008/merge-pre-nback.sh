python -u /REPO/src/CONN/prep.py /INPUTS /OUTPUTS

# Make mat files for covariates and contrasts
if [ -f "/INPUTS/covariates.csv" ]; then
	# convert covars to mat file for CONN
	python -u /REPO/src/CONN/covariate_csv2mat.py

	# Create the contrasts file
	python -u /REPO/src/CHAMP-A008/make_contrasts_nback.py
else
	echo "No covariates file found:/INPUTS/covariates.csv"
fi
