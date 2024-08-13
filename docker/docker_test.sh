TESTDIR=/Users/boydb1/TEST-ccmvumc_analyses
REPODIR=/Users/boydb1/git/ccmvumc-analyses

docker run -v $TESTDIR/INPUTS:/INPUTS -v $TESTDIR/OUTPUTS:/OUTPUTS -v $REPODIR:/REPO bud42/ccmvumc_analyses:v2 /bin/bash /REPO/src/DSCHOL-A003/main.sh

