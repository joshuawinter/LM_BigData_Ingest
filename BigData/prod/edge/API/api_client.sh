#!/bin/bash
#
# Get API data into a Flume spooldir, in JSON format.
#
# Run via cron, scheduled far enough after midnight that the source has all
# of yesterday's data available.
#
# Run without options, or with -h to get the required and optional parameters.
#
# Restrict access to the configuration files to the cron job user, since these
# will contain login information.
#

#
# Right now, the script can recover from missing some number of days
# but it does not handle any sort of failover to/from the other edge node.

# set -e makes bash exit immediately when a command fails.
set -e
# Cron will then send an email to the scheduled user.

# Initialize our own variables:
DEB=""
CNF=""
TMP=""
DST=""
GEO=""
KEY=""

usage() {
    echo "Usage: $0 [-d] [-g|-k] [-c /path/conf/file] -t /data/temp \\"
    echo "          -f /data/flume (bing|google|mediaalpha)"
    echo -e "\t-g|-k are run only the geography or keyword extract"
    echo -e "\t-c points to the bing.ini or google.yaml file"
    echo -e "\tthe temp (-t) directory MUST be on the same file system as"
    echo -e "\t\tthe output (-f) directory"
    echo -e "\t-f is the flume spooldir, not a file name"
}

while getopts "h?dgkc:f:t:" opt; do
    case "$opt" in
    h|\?)
        usage
        exit 2
        ;;
    d) # debug
        set -x
        DEB="-d"
        ;;
    c) # Configuration file
        CNF=$OPTARG
        ;;
    t) # temporary directory
        TMP=$OPTARG
        ;;
    f) # Flume listener directory
        DST=$OPTARG
        ;;
    g) # Get the geography report only
        GEO="g"
        ;;
    k) # Get the keyword report only
        KEY="k"
        ;;
    esac
done
shift $(expr $OPTIND - 1)
SRC=$1

if [ $# -ne 1 -o -z "$TMP" -o -z "$DST" ] ; then
    usage
    exit 1
fi

# Any new API clients would get added here, as well as usage().
if [ "$SRC" = 'bing' ] ; then
   ARG="-p -u"
    if [ -x /usr/bin/Bing.py ] ; then
        PRG=/usr/bin/Bing.py
    else
        PRG=/usr/local/bin/Bing.py
    fi
elif [ "$SRC" = 'google' ] ; then
    ARG=
    if [ -x /usr/bin/Google.py ] ; then
        PRG=/usr/bin/Google.py
    else
        PRG=/usr/local/bin/Google.py
    fi
elif [ "$SRC" = 'mediaalpha' ] ; then
    PRG=/usr/bin/wget
else
    usage
    exit 3
fi

client() {
    if [ $# -ne 1 ] ; then
        echo "Usage: client (-g|-k|-m)"
        exit 4
    fi
    TYP=$1

    RANGE=""
    if [ $SRC = 'bing' ] ; then
        # Yesterday is the default data retrieval request.
        YESTERDAY=`/bin/date -d yesterday +%F`
        # If we have run before,
        if [ -e $TMP/.$PRG$TYP ] ; then
            LAST=`/bin/cat $TMP/.$PRG$TYP`
            DAYBEFORE=`/bin/date -d "-2 days" +%F`
            # and the last run was not yesterday,
            if [ $DAYBEFORE != $LAST ] ; then
                # then run a range of dates for today's run.
                START=`/bin/date -d "$LAST +1 day" +%F`
                RANGE="-b $START -e $YESTERDAY"
            fi
        fi
    elif [ $SRC = 'mediaalpha' ] ; then
        # Yesterday is the default data retrieval request.
        YESTERDAY=`/bin/date -d yesterday +%F`
        # If we have run before,
        if [ -e $TMP/.$PRG$TYP ] ; then
            LAST=`/bin/cat $TMP/.$PRG$TYP`
            DAYBEFORE=`/bin/date -d "-2 days" +%F`
            # and the last run was not yesterday,
            if [ $DAYBEFORE != $LAST ] ; then
                # then run a range of dates for today's run.
                START=`/bin/date -d "$LAST +1 day" +%F`
                RANGE="date_from=${START}&date_to=${YESTERDAY}"
            fi
        fi
        if [ -z "$RANGE" ] ; then
            RANGE="date_from=${YESTERDAY}&date_to=4{YESTERDAY}"
        fi
    elif [ $SRC = 'google' ] ; then
        # Google doesn't have yesterday's data yet.
        YESTERDAY=`/bin/date -d "-2 days" +%F`
        # If we have run before,
        if [ -e $TMP/.$PRG$TYP ] ; then
            LAST=`/bin/cat $TMP/.$PRG$TYP`
            DAYBEFORE=`/bin/date -d "-3 days" +%F`
            # and the last run was not yesterday,
            if [ $DAYBEFORE != $LAST ] ; then
                # then run a range of dates for today's run.
                START=`/bin/date -d "$LAST +1 day" +%F`
                RANGE="-b $START -e $YESTERDAY"
            else
                RANGE="-b $YESTERDAY -e $YESTERDAY"
            fi
        fi
    fi

    # Build a temporary output file name. We give flume a unique, but
    # human-readable name by use of a full date-time with timezone on the
    # off-chance a daylight savings time change hits the same value two
    # hours in a row. The API clients will output to the given file name.
    DAT=`/bin/date +%FT%T%z`
    OUT=`/bin/mktemp $TMP/$SRC-$TYP-$DAT.XXXXXXXX`
    # Run the API client.
    if [ $SRC = 'mediaalpha' ] ; then
        /usr/bin/wget -O $OUT "https://insurance-exchange.mediaalpha.com/report.json?advertiser_id=46&channel_id=0&model_private=1&exclude_publisher_id=0&model_public=1&campaign_id=0&model_dsp=1&exclude_campaign_id=0&view=date&placement_id=0&product=0&publisher_id=0&token=GsW9WG6xTqfJokrrdS0GIy&$RANGE"
    else
        /usr/bin/python $PRG $DEB -c $CNF $ARG $TYP $RANGE $OUT
    fi

    # Make the atomic flip for Flume to take data.
    if [ -s $OUT ] ; then
        /bin/chmod 664 $OUT
        /bin/mv $OUT $DST
    else
        /bin/rm $OUT
    fi

    echo $YESTERDAY >$TMP/.$SRC$TYP
}

if [ "$SRC" = 'mediaalpha' ] ; then
    client -m
else
    if [ "$KEY" != "k" ] ; then
        # Get the geography report.
        client -g
    fi
    if [ "$GEO" != "g" ] ; then
        # Get the keyword report.
        client -k
    fi
fi
