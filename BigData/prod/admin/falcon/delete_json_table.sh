#!/bin/bash
exec > >(tee /tmp/delete_json_table.log)
exec 2>&1

if [ $# -ne 1 ] ; then
    echo "Usage: $0 table_name"
    exit 2
fi
tab=$1
out=`/usr/bin/hive -e "add jar hdfs://hdp001-nn:8020/apps/hive/json-serde-1.1.9.2-Hive13.jar; DROP TABLE $tab;" 2>&1`
rval=$?
if [ $rval -ne 0 ] ; then
    echo -n "failed to drop table $tab on "
    date
    echo $out
    exit $rval
fi
echo -n "dropped $tab on "
date
exit 0
