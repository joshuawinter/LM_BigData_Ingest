#!/bin/bash
exec > >(tee /tmp/json_to_table.log)
exec 2>&1

out=`/usr/bin/python json_to_table.py "$@"`
rval=$?
if [ $rval -ne 0 ] ; then
    echo -n "json_to_table.py $@ failed on "
    date
    echo $out
    exit $rval
fi
echo -n "json_to_table.py $@ on "
date
exit 0
