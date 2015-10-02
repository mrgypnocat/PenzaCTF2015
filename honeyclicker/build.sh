#!/bin/sh
START_TIME=`date +%s`

COMMIT_ID=`git --no-pager log --format="%H" -n 1`
BUILD_DATE=`date -u +%d.%m.%Y`
BUILD_TIME=`date -u +%H:%M:%S`

LDFLAGS="-X main.COMMIT_ID ${COMMIT_ID}"
LDFLAGS+=" -X main.BUILD_DATE ${BUILD_DATE}"
LDFLAGS+=" -X main.BUILD_TIME ${BUILD_TIME}"

export GOPATH=$(realpath ./)

#go build -ldflags "${LDFLAGS}" -o path/to/binary src/source/source.go
go build -o release/honeyclicker src/honeyclicker/service/*.go

go build -o checker/honeyclicker_checker src/honeyclicker/checker/*.go

checker/honeyclicker_checker gen
mv honey_pub.pem release/
mv honey_priv.pem checker/

END_TIME=`date +%s`
RUN_TIME=$((END_TIME-START_TIME))
echo "Build done in ${RUN_TIME}s"
