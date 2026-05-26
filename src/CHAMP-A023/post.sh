set -x

echo "POST!"

# Go to subjects folder
cd /OUTPUTS/SUBJECTS

# Run post steps
python -u /REPO/src/CHAMP-A023/post.py
