#!/usr/bin/python

"""
@author: Alan Brenner, n0255159 <alan.brenner@teradata.com>
"""

import datetime
import logging
from subprocess import Popen, PIPE, STDOUT

logging.basicConfig() # Stops "No handlers could be found...." message.


json_jar = 'hdfs://hdp001-nn:8020/apps/hive/json-serde-1.1.9.2-Hive13.jar'
# "/var/lib/hadoop-hdfs/json-serde-1.1.9.2-Hive13.jar"
partition_field = 'TimePeriod'


class JSONtoTableError(ValueError):
    pass


class JSONtoTable(object):
    """
    Copy data from a non-partitioned table into a date partitioned table.
    """

    # Errors and debugging.
    logger = logging.getLogger("JSONtoTable")

    dates = (
             ('%Y-%m-%dT%H:%M:%S', 'year', 'month', 'day', '-', 2),
             ('%Y-%m-%d %H:%M:%S', 'year', 'month', 'day', '-', 2),
             ('%m/%d/%Y %I:%M:%S %p', 'month', 'day', 'year', '/', 1),
             ('%Y-%m-%d', 'year', 'month', 'day', '-', 2),
             ('%m/%d/%Y', 'month', 'day', 'year', '/', 1),
            )

    def __init__(self, args, debug=False, json=json_jar,
                 partition=partition_field):
        self.json_tab = args[0]
        self.table = args[1]
        print len(args)
        self.types = {}
        for arg in args[2:]:
            parts = [ii.strip() for ii in arg.split('--')]
            if len(parts) > 1:
                self.types[parts[0].split()[0]] = parts[-1]
        if debug:
            self.logger.setLevel(logging.DEBUG)
        if json:
            self.json_jar = json
        else:
            self.json_jar = json_jar
        self.partition = partition
        self.logger.debug("json_jar = %s" , self.json_jar)
        self.logger.debug("table = %s", self.table)
        self.logger.debug("json table = %s", self.json_tab)
        self.logger.debug("partition by = %s", self.partition)
        self.selform = None
        self.seldate = None

    def run_hive(self, hql):
        """
        Run the given HQL, and capture all output.

        @param hql: statement(s) to run
        @type hql: string
        @return: all output from hive
        @rtype: string 
        @raise JSONtoTableError: on any error from hive
        """
        self.logger.debug(hql)
        job = Popen('/usr/bin/hive -e "%s"' % hql,
                    executable='/bin/sh', shell=True, stdout=PIPE, stderr=STDOUT)
        output = job.communicate()
        if job.returncode != 0:
            raise JSONtoTableError("%d in run_hive: %s" % (job.returncode, output))
        return output[0]

    def parse_dates(self, lines):
        """
        Extract at least one date after the OK line, or fail.

        @param lines: hive output split on newlines
        @type lines: array
        @return: start and stop datetimes
        @rtype: array of two items
        @raise JSONtoTableError: on failure to find any date 
        """
        found = False
        start = None
        stop = None
        for line in lines:
            ln = line.strip()
            if ln == "OK":
                found = True
                continue
            if ln.startswith('Time taken'):
                break
            if found and len(ln) > 0 and not ln.startswith("NULL"):
                date = None
                if self.selform is not None:
                    try:
                        date = datetime.datetime.strptime(ln, self.selform[0])
                    except ValueError:
                        self.selform = None
                if self.selform is None:
                    for ii in self.dates:
                        try:
                            date = datetime.datetime.strptime(ln, ii[0])
                            self.selform = ii
                            self.logger.info("Using date format %s", self.selform[0])
                            break
                        except ValueError:
                            continue
                if self.selform is None:
                    raise JSONtoTableError("unparse-able date at %s" % ln)
                if start is None:
                    start = date
                    stop = date
                elif date < start:
                    start = date
                elif date > stop:
                    stop = date
        if start is None:
            lines.extend(self.run_hive("describe %s;" % (self.json_tab, )).split("\n"))
            lines.extend(self.run_hive("select * from %s limit 2;" % (self.json_tab, )).split("\n"))
            raise JSONtoTableError("failed to find time periods in input %r" %
                                   lines)
        self.logger.debug("start = %r; stop = %r", start, stop)
        return start, stop

    def get_dates(self):
        """
        Get TimePeriods for the JSON table, and pass to parse_dates.

        @return: return value from parse_dates
        @rtype: list
        """
        hql = "add jar %s; select distinct(%s) from %s;" % (self.json_jar,
                                                            self.partition,
                                                            self.json_tab)
        output = self.run_hive(hql)
        return self.parse_dates(output.split("\n"))

    def get_fields(self):
        """
        Pull field names from the target Hive table.
        """
        hql = "describe {s.table};".format(s=self)
        lines = self.run_hive(hql).split("\n")
        fields = []
        found = False
        for line in lines:
            if line.strip() == 'OK':
                found = True
                continue
            if line.startswith('date_partition'):
                break
            if found:
                parts = [ii.strip().lower() for ii in line.split('\t')]
                if parts[0].endswith('_iso') and parts[1] == 'string':
                    fields.append("from_unixtime(unix_timestamp(%s, '%s'))" % (parts[0][0:-4], self.selform[0]))
                elif parts[0].endswith('_int') and parts[1] == 'bigint':
                    fields.append("unix_timestamp(%s, '%s')" % (parts[0][0:-4], self.selform[0]))
                elif parts[1] == 'double':
                    fields.append("CASE WHEN substr(%s, 0, 1) == '$' THEN DOUBLE(substr(%s, 1))" % (parts[0], parts[0]) + \
                                  "     WHEN substr(%s, -1) == '%%' THEN DOUBLE(substr(%s, -1)) / 100.0" % (parts[0], parts[0]) + \
                                  "     ELSE DOUBLE(%s) END" % (parts[0], ))
                elif parts[1] != 'string':
                    fields.append("%s(%s)" % (parts[1], parts[0]))
                else:
                    fields.append(parts[0])
        return ', '.join(fields)

    def copy_days(self):
        """
        Copy data from the source to partitions in the target.

        Bing's TimePeriod is not 0 padded on day or month, so we have to figure
        out the minimum and maximum dates in a data set by hand.

        @raise JSONtoTableError: on any error from hive
        """
        start, stop = self.get_dates()
        fields = self.get_fields()
        day = datetime.timedelta(days=1)
        stop += day
        while start < stop:
            if self.selform[5] == 1:
                self.seldate = self.selform[4].join(('%d' % getattr(start, self.selform[1]),
                                                     '%d' % getattr(start, self.selform[2]),
                                                     '%d' % getattr(start, self.selform[3])))
            else:
                self.seldate = self.selform[4].join(('%02d' % getattr(start, self.selform[1]),
                                                     '%02d' % getattr(start, self.selform[2]),
                                                     '%02d' % getattr(start, self.selform[3])))
            hql = """add jar {s.json_jar};
INSERT INTO TABLE {s.table} PARTITION(date_partition='{d.year}-{d.month:02}-{d.day:02}')
 SELECT {f} FROM {s.json_tab} WHERE instr({s.partition}, '{s.seldate}') = 1;
""".format(d=start, s=self, f=fields)
            self.run_hive(hql)
            start += day

    def run(self):
        """
        Run the copy method.

        @raise JSONtoTableError: on any error from hive
        """
        self.copy_days()


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog [options] source_table target_table")
    parser.add_option('-d', '--debug', action='store_true', dest='debug',
                      default=False, help='Output in-process data')
    parser.add_option('-j', '--json', dest='json', default=json_jar,
                      help='Path to JSON SerDe jar (default = %s)' % json_jar)
    parser.add_option('-f', '--datefield', dest='datefield', default=partition_field,
                      help='Field name to use for date partitioning (default = %s)' % partition_field)
    (options, args) = parser.parse_args()
    if len(args) < 2:
        parser.error("incorrect number of arguments")
    client = JSONtoTable(args, debug=True, json=options.json, #options.debug
                         partition=options.datefield)
    client.copy_days()
