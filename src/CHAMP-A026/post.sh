set -x

echo "POST!"

# Go to subjects folder
cd /OUTPUTS/SUBJECTS

# Run post steps
python -u /REPO/src/CHAMP-A026/post.py /OUTPUTS/SUBJECTS /OUTPUTS/report.pdf

# Remove subjects folder so we avoid uploading
rm -r /OUTPUTS/SUBJECTS
