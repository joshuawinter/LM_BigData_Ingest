#!/bin/bash
exec > >(tee /tmp/create_hive_table.log)
exec 2>&1

echo $0 "$@"

if [ $# -lt 3 ] ; then
    echo "Usage: $0 table_name location fields"
    exit 1
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
    echo -n "table $tab already exists on "
    date
    exit 0
fi

def=`/usr/bin/python get_hive_names.py "$*"`
echo $def
out=`/usr/bin/hive -e "CREATE TABLE $tab ($def) PARTITIONED BY (date_partition STRING) STORED AS RCFILE LOCATION '$loc';" 2>&1`
rval=$?
if [ $rval -ne 0 ] ; then
    echo -n "failed to create table $tab at $loc with $@ on "
    date
    echo $out
    exit $rval
fi
echo -n "table $tab created on "
date
exit 0
