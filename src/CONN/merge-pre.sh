
# convert covars to mat file for CONN
if [ -f "/INPUTS/covariates.csv" ]; then
	python /REPO/src/CONN/covariate_csv2mat.py
else
	echo "File not found /INPUTS/covariates.csv"
fi
