set -x

echo "POST!"

# Go to subjects folder
cd /OUTPUTS/DATA/SUBJECTS

# Run post steps
python -u /REPO/src/CHAMP-A023/post.py
