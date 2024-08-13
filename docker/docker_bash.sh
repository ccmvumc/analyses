TESTDIR=/Users/boydb1/TEST-ccmvumc_analyses
REPODIR=/Users/boydb1/git/ccmvumc-analyses

docker run \
-ti \
--rm \
--entrypoint /bin/bash \
-v $TESTDIR/INPUTS:/INPUTS \
-v $TESTDIR/OUTPUTS:/OUTPUTS \
-v $REPODIR:/REPO \
bud42/ccmvumc_analyses:v2

