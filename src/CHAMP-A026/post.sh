set -x

echo "POST!"

# Go to subjects folder
cd /OUTPUTS/SUBJECTS

# Run post steps
python -u /REPO/src/CHAMP-A026/report.py /OUTPUTS/SUBJECTS /OUTPUTS/report.pdf
python -u /REPO/src/CHAMP-A026/stats.py /OUTPUTS/SUBJECTS /OUTPUTS/stats.csv

# Remove subjects folder so we avoid uploading
rm -r /OUTPUTS/SUBJECTS
