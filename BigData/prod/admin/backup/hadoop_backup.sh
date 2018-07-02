#!/bin/sh
# @author: Alan Brenner <alan.brenner@teradata.com>

hostn=`/bin/hostname`
today=`/bin/date +%F`
logf=/tmp/backup.log
cd /

if `/bin/echo ${hostn} | /usr/bin/grep -q 'LMPH01'` ; then # production cluster
    BIP1=vxpip-phagnt01.lmig.com # 10.176.200.28
    BIP2=vxpip-phagnt01.lmig.com # 10.176.200.29
else    # dev cluster
    BIP1=vxkid-phagnt01.lmig.com # 10.182.200.135
    BIP2=vxkid-phagnt02.lmig.com # 10.182.200.136
fi

if [ ! -d /backup/postgres ] ; then
    /bin/mkdir -p /backup/postgres
    /bin/chown postgres:postgres /backup/postgres
fi

/bin/rm /backup/postgres/pg_dump* 
pgd="/backup/postgres/pg_dumpall_${hostn}_${today}.sql"
/usr/bin/sudo -u postgres /usr/bin/pg_dumpall --file="$pgd"
/usr/bin/scp "$pgd" dw_edge@${BIP1}:/agents/backups >>$logf 2>&1
/usr/bin/scp "$pgd" dw_edge@${BIP2}:/agents/backups >>$logf 2>&1

/bin/rm /backup/hadoop_conf*
hdp="/backup/hadoop_conf_${hostn}_${today}.tar.gz"
/bin/tar -czf "$hdp" etc/ambari* etc/falcon etc/flume etc/hadoop etc/hbase \
    etc/hive* etc/oozie etc/pig etc/postgresql etc/sqoop etc/zookeeper \
    data/hadoop/hdfs/namenode
/usr/bin/scp "$hdp" dw_edge@${BIP1}:/agents/backups >>$logf 2>&1
/usr/bin/scp "$hdp" dw_edge@${BIP2}:/agents/backups >>$logf 2>&1

logb=/tmp/backup_${hostn}_${today}.log
/bin/mv $logf $logb
/usr/bin/scp $logb dw_edge@${BIP1}:/agents/backups >$logf 2>&1 # > write new log
/usr/bin/scp $logb dw_edge@${BIP2}:/agents/backups >>$logf 2>&1
/bin/rm $logb
