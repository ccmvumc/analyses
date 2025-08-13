set -x

pip -q install matplotlib-venn

pip -q install pypdf 

cd /REPO/src/DnSeg/compare

python -u compare_dnseg_sclimbic.py /INPUTS /OUTPUTS
