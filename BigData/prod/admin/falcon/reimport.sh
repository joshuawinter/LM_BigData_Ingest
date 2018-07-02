#!/bin/sh

ID=`/usr/bin/id -n -u`
if [ $ID != 'hdfs' ] ; then
    echo "$0 must be run as hdfs"
    exit 1
fi

if [ $# -ne 1 ] ; then
    echo "Usage: $0 table"
    exit 2
fi
TAB=$1

if `/usr/bin/hive -e 'show tables;' 2>&1 | grep -q "^$TAB$"` ; then
    echo /usr/bin/hive -e "drop table $TAB;"
    RVAL=$?
    if [ $RVAL -ne 0 ] ; then
        echo "failed to delete table $TAB"
        exit $RVAL
    fi
fi

if `/usr/bin/hadoop fs -test -e /lz/marketing/b2b/$TAB` ; then
    PATH=/lz/marketing/b2b/$TAB
elif `/usr/bin/hadoop fs -test -e /lz/marketing/api/$TAB` ; then
    PATH=/lz/marketing/api/$TAB
else
    echo "Cannot find $TAB in /lz"
    exit 3
fi
START=`/bin/date +%Y-%m-%d`-04

ITEMS=`/usr/bin/hadoop fs -ls $PATH 2>/dev/null | /usr/bin/wc -l`
if [ $ITEMS -ne 0 ] ; then
    /usr/bin/hadoop fs -mkdir /tmp/reload_$TAB_$$
    /usr/bin/hadoop fs -mv $PATH/* /tmp/reload_$TAB_$$
    /usr/bin/hadoop fs -ls /tmp/reload_$TAB_$$ 2>/dev/null | /bin/sed -e 's/.*\/\([^/]*\)$/\1/' | while read entry ; do
        echo /usr/bin/hadoop fs -mv /tmp/reload_$TAB_$$/$entry $PATH/$START"
        # UNCOMMENT THE NEXT LINE TO ACTUALLY RUN
        #/usr/bin/hadoop fs -mv /tmp/reload_$TAB_$$/$entry $PATH/$START"
        NOW=`echo $START | /bin/sed -e 's/-\([0-2][0-9]\)$/ \1/'`
        START=`/bin/date -d "$NOW +1 hour" +%Y-$m-%d-%H`
    done
    # COMMENT THE NEXT LINE TO ACTUALLY RUN
    /usr/bin/hadoop fs -mv /tmp/reload_$TAB_$$/* $PATH
    /usr/bin/hadoop fs -rmdir /tmp/reload_$TAB_$$
fi

ARCH=`echo $PATH | /bin/sed -e 's/^\/lz/\/archive\/project/'`
ITEMS=`/usr/bin/hadoop fs -ls $PATH 2>/dev/null | /usr/bin/wc -l`
if [ $ITEMS -ne 0 ] ; then
    /usr/bin/hadoop fs -ls $ARCH 2>/dev/null | /bin/sed -e 's/.*\/\([^/]*\)$/\1/' | while read entry ; do
        echo /usr/bin/hadoop fs -mv $ARCH/$entry $PATH/$START"
        # UNCOMMENT THE NEXT LINE TO ACTUALLY RUN
        #/usr/bin/hadoop fs -mv $ARCH/$entry $PATH/$START"
        NOW=`echo $START | /bin/sed -e 's/-\([0-2][0-9]\)$/ \1/'`
        START=`/bin/date -d "$NOW +1 hour" +%Y-$m-%d-%H`
    done
fi
