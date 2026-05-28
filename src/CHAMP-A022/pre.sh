python -u /REPO/src/CONN/prep.py /INPUTS /OUTPUTS

# Make mat files for covariates and contrasts
if [ -f "/INPUTS/covariates.csv" ]; then
	# convert covars to mat file for CONN
	python -u /REPO/src/CONN/covariate_csv2mat.py

	# Create the contrasts file
	python -u /REPO/src/CHAMP-A022/make_contrasts.py /INPUTS/covariates.csv /OUTPUTS/contrasts.mat
else
	echo "No covariates file found:/INPUTS/covariates.csv"
fi
