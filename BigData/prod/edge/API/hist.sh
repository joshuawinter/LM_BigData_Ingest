#!/bin/sh

set -e

byday() {
	mon=`echo $1 | cut -f1-2 -d-`
	day=`echo $1 | cut -f3 -d-`
        if [ ! -d $HOME/Bing ] ; then
                mkdir $HOME/Bing
        fi
	ii=1
	while [ $ii -le $day ]
	do
		if [ $ii -lt 10 ]
		then
			b=0$ii
		else
			b=$ii
		fi
		python Bing.py -v -c ../../../../bing.ini -u -p -k -b $mon-$b -e $mon-$b $HOME/Bing/$mon-$b-keyword.json &
		python Bing.py -v -c ../../../../bing.ini -u -p -g -b $mon-$b -e $mon-$b $HOME/Bing/$mon-$b-geog.json &
		let ii=$ii+1
	done
	wait
        /usr/bin/bzip2 $HOME/Bing/$mon-*-geog.json &
        /usr/bin/bzip2 $HOME/Bing/$mon-*-keyword.json &
}

bymonth() {
	mon=`echo $1 | cut -f1-2 -d-`
	if [ ! -d $HOME/Bing ] ; then
		mkdir $HOME/Bing
	fi
	python Bing.py -v -c ../../../../bing.ini -u -p -k -b $mon-01 -e $1 $HOME/Bing/$mon-keyword.json &
	python Bing.py -v -c ../../../../bing.ini -u -p -g -b $mon-01 -e $1 $HOME/Bing/$mon-geog.json &
	#if [ ! -d $HOME/Google ] ; then
	#	mkdir $HOME/Google
	#fi
	#python Google.py -c ../../google.yaml -k -b $mon-01 -e $1 | bzip2 -c >$HOME/Google/$mon-keyword.bz2
        #python Google.py -c ../../google.yaml -g -b $mon-01 -e $1 | bzip2 -c >$HOME/Google/$mon-geog.bz2
}

#byday 2014-11-10
byday 2014-10-31
byday 2014-09-30
byday 2014-08-31
byday 2014-07-31
byday 2014-06-30
byday 2014-05-31
byday 2014-04-30
byday 2014-03-31
byday 2014-02-28
byday 2014-01-31

#byday 2013-12-31
#byday 2013-11-30
#byday 2013-10-31
#byday 2013-09-30
#byday 2013-08-31
#byday 2013-07-31
#byday 2013-06-30
#byday 2013-05-31
#byday 2013-04-30
#byday 2013-03-31
#byday 2013-02-28
#byday 2013-01-31

#bymonth 2012-12-31
#bymonth 2012-11-30
#bymonth 2012-10-31
#bymonth 2012-09-30
#bymonth 2012-08-31
#bymonth 2012-07-31
#bymonth 2012-06-30
#bymonth 2012-05-31
#bymonth 2012-04-30
#bymonth 2012-03-31
#bymonth 2012-02-28
#bymonth 2012-01-31

wait
