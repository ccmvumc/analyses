# merge
echo "Merging CONN projects"
xvfb-run \
-e /OUTPUTS/xvfb.err -f /OUTPUTS/xvfb.auth \
-a --server-args "-screen 0 1600x1200x24" \
/opt/conn/run_conn.sh \
/opt/mcr/v912 batch \
/REPO/src/CONN/merge.m

# covars
echo "Loading covariates to CONN project"
xvfb-run \
-e /OUTPUTS/xvfb.err -f /OUTPUTS/xvfb.auth \
-a --server-args "-screen 0 1600x1200x24" \
/opt/conn/run_conn.sh \
/opt/mcr/v912 batch \
/REPO/src/CONN/load_covariates.m

rm /OUTPUTS/xvfb.auth /OUTPUTS/xvfb.err

echo "ALL DONE!"
