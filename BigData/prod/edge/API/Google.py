#!/usr/bin/env python2.6
'''
This application expects the user name, password, and
developer token to be provided in the source below.

Command line usage: python Google.py -

Created on Jul 2, 2014

@author: n0083510 'Parsons, Joshua 0055' <JOSHUA0055.PARSONS@libertymutual.com>
@author: ab186069 'Alan Brenner' <alan.brenner@teradata.com> or n0255159

'''
from datetime import datetime
from googleads import adwords
import logging
import json
import os
import sys
import tempfile



clients = (
           ('597-119-6487', 'Global Accident and Health'),
           ('231-340-3778', 'Liberty Mutual - Affinity', 'Liberty Mutual - Agency One To One Interactive'),
           ('900-844-0374', 'Liberty Mutual - Auto', 'Digitas, Inc.'),
           ('329-020-6472', 'Liberty Mutual - Be Fire Smart', 'Digitas, Inc.'),
           ('285-942-2878', 'Liberty Mutual - Brand', 'Digitas, Inc.'),
           ('223-947-2640', 'Liberty Mutual - Health', 'Digitas, Inc.'),
           ('189-532-2825', 'Liberty Mutual - Home', 'Digitas, Inc.'),
           ('751-750-9476', 'Liberty Mutual - Learn Return', 'Liberty Mutual - Agency One to One Interactive'),
           ('315-064-9537', 'Liberty Mutual - Mobile', 'One to One Interactive'),
           ('835-796-5825', 'Liberty Mutual - Renters', ''),
           ('677-787-3329', 'Liberty Mutual - Responsible Sports', 'Digitas, Inc.'),
           ('515-007-7034', 'Liberty Mutual - Safety & Security', 'Digitas, Inc.'),
           ('515-007-7034', 'Liberty Mutual - YouTube', 'Hill Holliday'),
           )




__prog__ = 'Google.py'
__release__ = '1.0'
__now__ = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

logging.basicConfig() # Stops "No handlers could be found...." message.

class Google(object):
    """
    Extract data from the Google Ad API server.
    """

    # Output ordering.
    columns = []

    # https://developers.google.com/adwords/api/docs/appendix/reports
    # general schema definitions and data types for reports
    keywordReportColumns = ['Date', # segment, Day
                            'AdNetworkType1', # segment, Network
                            'Device', # segment, Device
                            'AccountDescriptiveName', # attribute, Account
                            'CustomerDescriptiveName', # attribute, Client name
                            'PrimaryCompanyName', # attribute, Company name
                            'CampaignId', # attribute, Campaign ID, long
                            'CampaignStatus', # attribute, Campaign state
                            'AdGroupName', # attribute, Ad group
                            'KeywordText', # attribute, Keyword
                            'KeywordMatchType', # attribute, Match type
                            'Status', # attribute, Keyword state
                            'QualityScore', # attribute, Quality score, integer
                            'DestinationUrl', # attribute, Destination URL
                            #'MaxCpc', # attribute, Max. CPC, double -- no longer available
                            'AverageCpc', # metric, Avg. CPC, double
                            'AverageCpm', # metric, Avg. CPM, double
                            'AveragePosition', # metric, Avg. position, double
                            'Impressions', # metric, Impressions, long
                            'Clicks', # metric, Clicks, long
                            'Cost', # metric, Cost, double
                            ]
    keywordReportTypes = {'CampaignId': 'i',
                          "QualityScore": 'i',
                          'MaxCpc': 'm',
                          'AverageCpc': 'm',
                          'AverageCpm': 'm',
                          "AveragePosition": 'f',
                          "Impressions": 'i',
                          "Clicks": 'i',
                          "Cost": 'm',
                          }

    geographyReportColumns = ['Date', # segment, Day
                              'AdNetworkType1', # segment, Network
                              'Device', # segment, Device
                              'AccountDescriptiveName', # attribute, Account
                              'CustomerDescriptiveName', # attribute, Client name
                              'PrimaryCompanyName', # attribute, Company name
                              'CountryCriteriaId', # attribute, Country/Territory
                              'RegionCriteriaId', # attribute, Region
                              'CityCriteriaId', # attribute, City
                              'MetroCriteriaId', # attribute, Metro area
                              'AdGroupName', # attribute, Ad group
                              'AdGroupStatus', # attribute, Ad group state
                              'CampaignId', # attribute, Campaign ID, long
                              'CampaignStatus', # attribute, Campaign state
                              'AveragePosition', # metric, Avg. position, double
                              'Impressions', # metric, Impressions, long
                              'Clicks', # metric, Clicks, long
                              'Cost', # metric, Cost, double
                              'Conversions', # metric, Converted clicks, long
                              ]
    geographyReportTypes = {'CampaignId': 'i',
                            "AveragePosition": 'f',
                            "Impressions": 'i',
                            "Clicks": 'i',
                            "Cost": 'm',
                            "Conversions": 'i',
                            }

    # Errors and debugging.
    logger = logging.getLogger("GoogleAPI")

    # Other command line options:
    path = '/etc/LM/google.yaml'
    keyword = False
    geography = False
    fields = False
    period = 'YESTERDAY'
    text = False
    debug = False
    meta = True

    colcount = None

    def __init__(self, **args):
        """
        @param args: use prod and/or debug as named parameters, if needed.
        @type args: dictionary
        """
        for key in args.iterkeys():
            if hasattr(self, key):
                setattr(self, key, args[key])
        if self.debug:
            self.logger.setLevel(logging.DEBUG)
        self.logger.debug("loading configuration from %s", self.path)

    def _submitGenerateReport(self, report, service):
        """
        Send a request to generate a report.

        @param report: the definition of the report request
        @type report: dictionary
        @return: ElementTree or None
        """
        self.logger.debug("_submitGenerateReport %r", report)
        tf = tempfile.NamedTemporaryFile(delete=False)
        downloader = None
        tries = 0
        while True:
            try:
                downloader = service.GetReportDownloader(version='v201406')
                break
            except Exception, err:
                self.logger.warn(err)
                tries += 1
                if tries > 3:
                    tf.close()
                    return tf.name
        try:
            downloader.DownloadReport(report, output=tf)
        except Exception, err:
            self.logger.warn(err)
        tf.close()
        return tf.name

    def _text(self, data):
        """
        Build a write-able output string.

        @param data: value(s) to format into a string
        @type data: dictionary
        @return: a newline ended string
        """
        if len(data) == 0:
            return "\n"
        rval = []
        for key in self.columns:
            rval.append(data[key])
        return ",".join(rval) + "\n"

    def _json(self, data):
        """
        Dump the input dictionary as a JSON object on a single line, or return
        an empty string if the input dictionary is empty.

        @param data: value(s) to format into a string
        @type data: dictionary
        @return: a newline ended string, or an empty string
        """
        if data is None or len(data) == 0:
            return ""
        if self.meta:
            data['meta_history'] = [{'prog': __prog__,
                                     'release': __release__,
                                     'author': __author__,
                                     'date': __now__},]
        return json.dumps(data) + "\n"

    def _split_line(self, line, columns, types):
        """
        Convert a line from the Google API document into a dictionary.
        """
        rval = {}
        parts = line.split("\t")
        if len(parts) != self.colcount:
            self.logger.debug("%d fields in %s", len(parts), line)
            return rval
        ii = 0
        for key in columns:
            #self.logger.debug("%d: %s = %s", ii, key, parts[ii])
            if types.has_key(key):
                if types[key] == 'i':
                    try:
                        rval[key] = int(parts[ii])
                    except ValueError:
                        self.logger.error("failed converting '%s' to int for '%s' in %s",
                                          key, parts[ii], line.strip())
                elif types[key] == 'f':
                    try:
                        rval[key] = float(parts[ii])
                    except ValueError:
                        self.logger.error("failed converting '%s' to float for '%s' in %s",
                                          key, parts[ii], line.strip())
                elif types[key] == 'm':
                    try:
                        if parts[ii] == ' --':
                            pass
                        elif parts[ii].find(':') > 0:
                            rval[key] = float(parts[ii].split(':')[1]) / 1000000.0
                        else:
                            rval[key] = float(parts[ii]) / 1000000.0
                    except ValueError:
                        self.logger.error("failed converting '%s' from money for '%s' in %s",
                                          key, parts[ii], line.strip())
                else:
                    self.logger.warn("unknown type for %s: %s", key, types[key])
            else:
                rval[key] = parts[ii]
            ii += 1
        return rval
'''
    def _accounts(self):
        rep_def = {'reportName': 'Account List',
                   'reportType': 'ACCOUNT_PERFORMANCE_REPORT',
                   'dateRangeType': 'YESTERDAY',
                   'downloadFormat': 'TSV',
                   'selector': {'fields': ['AccountDescriptiveName',
                                           'ExternalCustomerId',
                                           'Impressions']},
                   'includeZeroImpressions': 'true',
                   }
        tfn = self._submitGenerateReport(rep_def).split("\n")
        tf = open(tfn, 'rb')
        print tf.read()
        tf.close()
        os.unlink(tfn)
'''
    def _process(self, rname, rtype, columns, client, types, output):
        """
        Create a report, then output in the setup format.

        @param rname: report name
        @type rname: string
        @param rtype: One of the entries at
            https://developers.google.com/adwords/api/docs/appendix/reports
        @type rtype: string
        @param columns: list of field names from the specified report type
        @type columns: array of strings
        @param client: an entry from the module clients tuple
        @type tuple: tuple
        @param types: non-string data types: 'i' - int, 'f' - float
        @type types: dictionary
        @param output: use for outputing data
        @type output: file-like object (write method)
        """
        service = adwords.AdWordsClient.LoadFromStorage(self.path)
        service.client_customer_id = client[0]
        for ii in ('client_customer_id', 'developer_token', 'https_proxy',
                   'partial_failure', 'user_agent', 'validate_only'):
            self.logger.debug("%s = %r", ii, getattr(service, ii))
        if self.text:
            form_line = self._text
        else:
            form_line = self._json

        rep_def = {'reportName': rname,
                   'reportType': rtype,
                   'downloadFormat': 'TSV',
                   'selector': {'fields': columns},
                   }
        if isinstance(self.period, tuple):
            rep_def['dateRangeType'] = 'CUSTOM_DATE'
            rep_def['selector']['dateRange'] = {'min': self.period[0].strftime('%Y%m%d'),
                                                'max': self.period[1].strftime('%Y%m%d')}
        else:
            rep_def['dateRangeType'] = self.period
        #if rtype == 'KEYWORDS_PERFORMANCE_REPORT':
        #    rep_def['includeZeroImpressions'] = 'true'
        tfn = self._submitGenerateReport(rep_def, service)
        tf = None
        try:
            tf = open(tfn, 'rb')
            # Skip header lines
            line = tf.readline()
            if not line:
                return
            self.logger.debug("first line for %s, %s: %s", client[0], client[1], line)
            line = tf.readline()
            self.logger.debug("second line: %s", line)
            self.logger.debug("second line field count: %d", len(line.split("\t")))

            for line in tf:
                #self.logger.debug(line)
                if line.startswith("Total\t"): 
                    self.logger.debug("total line for %s, %s: %s", client[0], client[1], line)
                    break
                output.write(form_line(self._split_line(line, columns, types)))
        finally:
            if tf is not None:
                tf.close()
                os.unlink(tfn)


    def _report(self, rname, rtype, columns, types, output=None):
        """
        Spawn threads to download each client in parallel.

        @param rname: report name
        @type rname: string
        @param rtype: One of the entries at
            https://developers.google.com/adwords/api/docs/appendix/reports
        @type rtype: string
        @param columns: list of field names from the specified report type
        @type columns: array of strings
        @param types: non-string data types: 'i' - int, 'f' - float
        @type types: dictionary
        @param output: a path/prefix to use for output files
        @type output: string
        """
        self.logger.debug("_report")
        self.logger.debug(columns)
        self.colcount = len(columns)
        self.logger.debug("field count = %d", self.colcount)
        for client in clients:
            self._process(rname, rtype, columns, client, types, output)

    def _field_list(self, rtype):
        # Initialize appropriate service.
        service = adwords.AdWordsClient.LoadFromStorage(self.path)
        report_definition_service = service.GetService('ReportDefinitionService',
                                                       version='v201406')
        # Get report fields.
        fields = report_definition_service.getReportFields(rtype)
        # Display results.
        print 'Report type \'%s\' contains the following fields:' % rtype
        for field in fields:
            print ' - %s (%s)' % (field['fieldName'], field['fieldType']),
            if 'enumValues' in field:
                print ':= [%s]' % ', '.join(field['enumValues'])
            else:
                print

    def run(self, output):
        if self.fields:
            if self.keyword:
                self._field_list('KEYWORDS_PERFORMANCE_REPORT')
            elif self.geography:
                self._field_list('GEO_PERFORMANCE_REPORT')
        elif self.keyword:
            self._report('Keyword Report', 'KEYWORDS_PERFORMANCE_REPORT',
                         self.keywordReportColumns,
                         self.keywordReportTypes, output)
        elif self.geography:
            self._report('Geography Report', 'GEO_PERFORMANCE_REPORT',
                         self.geographyReportColumns,
                         self.geographyReportTypes, output)
        else:
            self.logger.warn("specify at least one of -g or -k")


def getReportingPeriod(begin, end, week, month, last):
    """
    Build the period parameter for Bing.__init__().
    ALL_TIME CUSTOM_DATE LAST_14_DAYS LAST_30_DAYS LAST_7_DAYS 
    LAST_BUSINESS_WEEK LAST_MONTH LAST_WEEK LAST_WEEK_SUN_SAT
    THIS_MONTH THIS_WEEK_MON_TODAY THIS_WEEK_SUN_TODAY TODAY

    YESTERDAY is the default.

    @param begin: ISO format date (YYYY-MM-DD)
    @type begin: string or None
    @param end:  ISO format date (YYYY-MM-DD)
    @type end: string or None
    @param week: if True, report for this or last week
    @type week: boolean
    @param month: if True, report for this or last month
    @type month: boolean
    @param year: if True, report for this or last year
    @type year: boolean
    @param last: if True, report for the last period, not this period
    @type last: boolean
    @return: string or tuple of two datetimes, default: "Yesterday"
    """
    if begin and end:
        rval = (datetime.strptime(begin, '%Y-%m-%d'),
                datetime.strptime(end, '%Y-%m-%d'))
    elif week or month:
        if last:
            rval = 'LAST'
        else:
            rval = 'THIS'
        if week:
            rval += '_WEEK'
        else:
            rval += '_MONTH'
        if rval == 'THIS_WEEK':
            rval = 'THIS_WEEK_SUN_TODAY'
    else:
        rval = 'YESTERDAY'
    return rval


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog [options] [output_files_pathprefix]")
    parser.add_option('-d', '--debug', action='store_true', dest='debug',
                      default=False, help='Output in-process data.')
    parser.add_option('-z', '--no-meta', action='store_false', dest='meta',
                      default=True,
                      help='if set, do not add processing metadata to JSON')
    parser.add_option('-c', '--config', action='store', dest='config', default=Google.path,
                      help='ini configuration file to use, defaults to ' + Google.path)
    parser.add_option('-t', '--text', action='store_true', dest='text',
                      default=False, help='Output text rather than JSON')
    parser.add_option('-k', '--keyword', action='store_true', dest='keyword',
                      default=False, help='Generate keyword report')
    parser.add_option('-g', '--geography', action='store_true', dest='geog',
                      default=False, help='Generate geography report')
    parser.add_option('-b', '--begin', dest='begin', default=None,
                      help='beginning date in ISO format YYYY-MM-DD')
    parser.add_option('-e', '--end', dest='end', default=None,
                      help='ending date in ISO format YYYY-MM-DD')
    parser.add_option('-w', '--week', action='store_true', dest='week',
                      default=False, help='(this|last) week')
    parser.add_option('-m', '--month', action='store_true', dest='month',
                      default=False, help='(this|last) month')
    parser.add_option('-l', '--last', action='store_true', dest='last',
                      default=False, help='last (week|month|year) instead of this')
    parser.add_option('-f', '--fields', action='store_true', dest='fields',
                      default=False, help='get available field list for given type')

    (opts, args) = parser.parse_args()
    if len(args) > 1:
        parser.error("incorrect number of arguments")
    client = Google(path=opts.config,
                    keyword=opts.keyword,
                    geography=opts.geog,
                    fields=opts.fields,
                    period=getReportingPeriod(opts.begin, opts.end, opts.week,
                                              opts.month, opts.last),
                    text=opts.text,
                    meta=opts.meta,
                    debug=opts.debug)
    output = sys.stdout
    if len(args) == 1 and args[0] != '-':
        output = open(args[0], 'wb')
    client.run(output)
