#!/bin/bash
#
# Move B2B landed data into a Flume spooldir, with a format change to JSON.
#
# Run via cron, scheduled just before a B2B file is expected.
#
# Run without options, or with -h to get the required and optional parameters.
#
# Created on Sep 30, 2014
#
# @author: Alan Brenner <alan.brenner@teradata.com> or alan.brenner@libertymutual.com
#
# TODO: run book directions to recover from errors.

# set -e makes bash exit immediately when a command fails.
set -e
# Cron will then send an email to the scheduled user.

# Initialize our own variables:
SRC=""
TYP=""
HDR=""
TMP=""
DEB=""
TAB=0
PIP=0
DST=""
ARC=3

usage() {
    echo "Usage: $0 [-d] [-y types] [-h headers] [-a archive] \\"
    echo "          -b /data/b2b -t /data/temp -f /data/flume"
    echo -e "\trequired parameters are directory paths"
    echo -e "\t\tthe temp (-t) directory MUST be on the same file system as"
    echo -e "\t\tthe output (-f) directory"
    echo -e "\tfor types:"
    echo -e "\t\ti = integer, f = float, b = boolean, default is s for string"
    echo -e "\t\tfor example: SourceID:i,Clicks:i,SerialNumber:i,Insured:b"
    echo -e "\tfor headers, an ordered list of field names:"
    echo -e "\t\tfor example: SourceID,Clicks,Impressions"
    echo -e "\tarchive is the number of old inputs to keep, defaulting to 3."
    echo -e "\t\t0 means none."
}

while getopts "h?dipb:y:h:f:t:a:" opt; do
    case "$opt" in
    h|\?)
        usage
        exit 2
        ;;
    d) # debug
        set -x
        DEB="-d"
        ;;
    b) # B2B should not put files directly into Flume directory.
        SRC=$OPTARG
        ;;
    y) # Data types in B2B file.
        TYP="-y $OPTARG"
        ;;
    h) # Header, if not in the input file.
        HDR="-r $OPTARG"
        ;;
    i) # Set this for tab delimiter (CTRL-I)
        TAB=1
        ;;
    p) # or pipe (default is comma).
        PIP=1
        ;;
    t) # temporary directory
        TMP=$OPTARG
        ;;
    f) # Flume listener directory
        DST=$OPTARG
        ;;
    a) # old input file copies
        ARC=$OPTARG
        ;;
    esac
done

if [ -z "$SRC" -o -z "$TMP" -o -z "$DST" ] ; then
    usage
    exit 1
fi

NAM=`/bin/basename $SRC`
# Handle tab or pipe options.
OPT=
if [ $TAB -ne 0 ] ; then
    OPT='-t'
elif [ $PIP -ne 0 ] ; then
    OPT='-p'
fi

FILE=0

process_file() {
	INP=$1
	# Build a temporary output file name. On success, this will be renamed to flume.
	OUT=`/bin/mktemp --tmpdir=$TMP`
	# Run the CSV to JSON converter.
	/usr/bin/python /usr/bin/delim_to_json.py $DEB $OPT $HDR $TYP $INP $OUT
	/bin/chmod 664 $OUT
	# Make the atomic flip for Flume to take data. We give flume a unique, but
	# human-readable name by use of a full date-time with timezone on the off-chance
	# a daylight savings time change hits the same value two hours in a row.
	DSTFILE="$DST/$NAM.$FILE.`/bin/date +%FT%T%z`"
	/bin/mv $OUT $DSTFILE
	let FILE=$FILE+1

	# Delete the input, if told to.
	if [ $ARC -eq 0 ] ; then
	    /bin/rm $INP
	    return
	fi

	# Otherwise, archive the input.
	if [ -e "$TMP/$NAM.$ARC" ] ; then
	    # Remove any existing max value, not to be kept anymore, file.
	    /bin/rm "$TMP/$NAM.$ARC"
	fi
	# Walk 2->3, 1->2.
	let jj=$ARC-1
	kk=$ARC
	while [ $jj -gt 0 ] ; do
	    if [ -e "$TMP/$NAM.$jj" ] ; then
	        /bin/mv "$TMP/$NAM.$jj" "$TMP/$NAM.$kk"
	    fi
	    kk=$jj
	    set +e
	    let jj=$jj-1
	    set -e
	done
	# Rename the input file as landed by B2B into the holding pattern.
	/bin/mv "$INP" "$TMP/$NAM.1"
}

# Wait for input.
declare -A FILES
found=0
ii=0
while [ $ii -lt 24 ] ; do
    B2B=`echo $SRC/*`
    if [ "$B2B" != "$SRC/*" ] ; then
    	# Get the last change date right now.
    	for file in $B2B ; do
	    	BAS=`basename $file`
	    	FILES[$BAS]=`/usr/bin/stat -c %Y "$file"`
	    done
	    # Wait 10 minutes.
	    sleep 600
	    # For each of the found files:
	    for file in $B2B ; do
	    	# If it still exists:
	    	if [ -e $file ] ; then
		    	BAS=`basename $file`
		        # Get the last change date again. Hopefully it is the same.
		        thismod=`/usr/bin/stat -c %Y "$file"`
		    	if [ ${FILES[$BAS]} = $thismod ] ; then
		    		# They are the same. This will remove the file from the
		    		# $SRC directory, so we won't find it again.
		    		process_file $file
		    		found=1
		    	fi
		    fi
	    done
	else
		if [ $found -eq 1 ] ; then
			break
		fi
		# Check for input files again in 10 minutes.
		sleep 600
	    let ii=$ii+1
    fi
done
if [ $ii -ge 24 -a $found -eq 0 ] ; then
    echo "timeout waiting for B2B input"
    exit 3
fi
