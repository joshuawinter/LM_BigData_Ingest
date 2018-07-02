#!/bin/bash
exec > >(tee /tmp/create_archive_directory.log)
exec 2>&1


if [ $# -ne 1 ] ; then
    echo "Usage: $0 path"
    exit 2
fi
path=`/usr/bin/dirname $1`
/usr/bin/hadoop fs -test -e $path
rval=$?
if [ $rval -eq 0 ] ; then
    echo -n "found $path on"
    date
    exit 0
fi
/usr/bin/hadoop fs -mkdir -p $path
rval=$?
if [ $rval -ne 0 ] ; then
    echo -n "failed to create $path on "
    date
    exit $rval
fi
/usr/bin/hadoop fs -test -e $path
rval=$?
if [ $rval -ne 0 ] ; then
    echo -n "failed to find $path after creation on "
    date
    exit $rval
fi
echo -n "created $path on"
date
exit 0
