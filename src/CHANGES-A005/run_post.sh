set -x

bash /REPO/src/CONN/merge-post-roi_only.sh

echo "Running post.py"

python -u /REPO/src/CHANGES-A005/post.py
