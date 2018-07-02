#!/bin/sh

if [ $# -ne 1 ] ; then
    echo "Usage: $0 input_name"
    exit 2
fi
nam=$1

for ii in archive lz process ; do
    xml=${ii}_${nam}.xml
    if [ ! -f $xml ] ; then
        echo "Cannot find $xml"
        exit 3
    fi
done

set -e
falcon entity -type process -name `grep process process_${nam}.xml | grep name | cut -f4 -d'"'` -delete
falcon entity -type feed -name `grep feed archive_${nam}.xml | grep name | cut -f4 -d'"'` -delete
falcon entity -type feed -name `grep feed lz_${nam}.xml | grep name | cut -f4 -d'"'` -delete

falcon entity -type feed -file archive_${nam}.xml -submitAndSchedule
falcon entity -type feed -file lz_${nam}.xml -submitAndSchedule
falcon entity -type process -file process_${nam}.xml -submitAndSchedule
