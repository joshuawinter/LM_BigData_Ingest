#!/bin/bash
exec > >(tee /tmp/create_json_table.log)
exec 2>&1

if [ $# -lt 3 ] ; then
    echo "Usage: $0 table_name location fields"
    exit 2
fi
tab=$1
shift
loc=$1
shift

tabs=`/usr/bin/hive -e 'show tables;'` 2>/dev/null
rval=$?
if [ $rval -ne 0 ] ; then
    echo -n "failed to get table list from Hive on "
    date
    echo $tabs
    exit $rval
fi
if `echo $tabs | grep -q -w $tab` ; then
    echo -n "really weird that table $tab already exists on "
    date
    exit -1
fi

JAR="add jar hdfs://hdp001-nn:8020/apps/hive/json-serde-1.1.9.2-Hive13.jar;"
ROW="ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'"
LOC="STORED AS TEXTFILE LOCATION '$loc';"
PRP=""

def=`/usr/bin/python get_json_names.py "$*"`
echo $def
map=`/usr/bin/python get_json_to_hive_map.py "$*"`
echo $map
if [ -n "$map" ] ; then
    PRP="WITH SERDEPROPERTIES ( $map )"
fi
echo /usr/bin/hive -e "$JAR CREATE EXTERNAL TABLE $tab ($def) $ROW $PRP $LOC" 2>&1
out=`/usr/bin/hive -e "$JAR CREATE EXTERNAL TABLE $tab ($def) $ROW $PRP $LOC" 2>&1`
rval=$?
if [ $rval -ne 0 ] ; then
    echo -n "failed to create $tab at $loc with $@ on "
    date
    echo $out
    exit $rval
fi
echo -n "created $tab on "
date
exit 0
