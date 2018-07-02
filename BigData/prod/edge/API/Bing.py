#!/usr/bin/env python2.6
'''
This application expects the user name, password, and
developer token to be provided in the source below.

Command line usage: python Bing.py

Created on Jul 2, 2014

@author: n0083510 'Parsons, Joshua 0055' <JOSHUA0055.PARSONS@libertymutual.com>
@author: ab186069 'Alan Brenner' <alan.brenner@teradata.com> or n0255159

{"accounts": [
    {"PauseReason": "2", "Number": "X0311904", "Id": "24079", "AccountLifeCycleStatus": "Pause", "Name": "Liberty Mutual Branding"},
    {"PauseReason": "2", "Number": "X1294501", "Id": "232099", "AccountLifeCycleStatus": "Pause", "Name": "Liberty Mutual_Be Fire Smart"},
    {"PauseReason": "2", "Number": "X1570183", "Id": "232391", "AccountLifeCycleStatus": "Pause", "Name": "Coach of the Year DO NOT USE"},
    {"PauseReason": "2", "Number": "X0861194", "Id": "232395", "AccountLifeCycleStatus": "Pause", "Name": "Responsible Sports DO NOT USE"},
    {"PauseReason": "", "Number": "X0902030", "Id": "233144", "AccountLifeCycleStatus": "Inactive", "Name": "Be Fire Smart DO NOT USE"},
    {"PauseReason": "2", "Number": "X0261916", "Id": "237673", "AccountLifeCycleStatus": "Pause", "Name": "Liberty Mutual_Coach of the Year"},
    {"PauseReason": "2", "Number": "X0620423", "Id": "237677", "AccountLifeCycleStatus": "Pause", "Name": "Liberty Mutual_Responsible Sports"},
    {"PauseReason": "2", "Number": "X1396983", "Id": "253834", "AccountLifeCycleStatus": "Pause", "Name": "Liberty Mutual Branding Main"},
    {"PauseReason": "2", "Number": "X0310480", "Id": "262694", "AccountLifeCycleStatus": "Pause", "Name": "Responsiblity Project"},
    {"PauseReason": "2", "Number": "X1261575", "Id": "294241", "AccountLifeCycleStatus": "Pause", "Name": "Liberty Mutual Educator"},
    {"PauseReason": "2", "Number": "X0175606", "Id": "304872", "AccountLifeCycleStatus": "Pause", "Name": "Teen Drivers"},
    {"PauseReason": "", "Number": "X0145471", "Id": "735123", "AccountLifeCycleStatus": "Active", "Name": "Liberty Mutual Brand"},
    {"PauseReason": "", "Number": "X1898989", "Id": "735141", "AccountLifeCycleStatus": "Active", "Name": "LM_Home Insurance"},
    {"PauseReason": "", "Number": "X0573057", "Id": "735156", "AccountLifeCycleStatus": "Active", "Name": "LM_Auto Insurance"},
    {"PauseReason": "", "Number": "X1365749", "Id": "735165", "AccountLifeCycleStatus": "Active", "Name": "LM_Renters Insurance"},
    {"PauseReason": "2", "Number": "X1502033", "Id": "735175", "AccountLifeCycleStatus": "Pause", "Name": "LM_Affinity"},
    {"PauseReason": "2", "Number": "X0902678", "Id": "761863", "AccountLifeCycleStatus": "Pause", "Name": "LM_Teen Drivers_OTO"},
    {"PauseReason": "2", "Number": "X0236988", "Id": "761874", "AccountLifeCycleStatus": "Pause", "Name": "LM_Be Fire Smart"},
    {"PauseReason": "2", "Number": "X0503517", "Id": "761876", "AccountLifeCycleStatus": "Pause", "Name": "LM_Learn Return_OTO"},
    {"PauseReason": "", "Number": "X0072868", "Id": "761884", "AccountLifeCycleStatus": "Active", "Name": "LM_Responsible Sports"},
    {"PauseReason": "2", "Number": "X0756542", "Id": "788948", "AccountLifeCycleStatus": "Pause", "Name": "LM_Coach of the Year_OTO"},
    {"PauseReason": "2", "Number": "X1379187", "Id": "1036285", "AccountLifeCycleStatus": "Pause", "Name": "LM_PLP_OTO"},
    {"PauseReason": "2", "Number": "X1709850", "Id": "1177789", "AccountLifeCycleStatus": "Pause", "Name": "LM_Senior Driving"},
    {"PauseReason": "2", "Number": "X0506643", "Id": "1203435", "AccountLifeCycleStatus": "Pause", "Name": "LM_Like My Community_OTO"},
    {"PauseReason": "", "Number": "X0063817", "Id": "1227033", "AccountLifeCycleStatus": "Active", "Name": "LM_Brand Mobile"},
    {"PauseReason": "4", "Number": "X0581581", "Id": "1385025", "AccountLifeCycleStatus": "Pause", "Name": "Affinity B2B"},
    {"PauseReason": "", "Number": "X7067459", "Id": "2273138", "AccountLifeCycleStatus": "Active", "Name": "LM_Safety & Security"},
    {"PauseReason": "", "Number": "B004BQMT", "Id": "34000050", "AccountLifeCycleStatus": "Active", "Name": "Liberty Mutual \u2013 Passion to Protect"},
    {"PauseReason": "2", "Number": "B004Z851", "Id": "34000282", "AccountLifeCycleStatus": "Pause", "Name": "Liberty Mutual Motorcycle"}],
  "CustomerId": "25245",
  "meta_history": [{"prog": "Bing.py", "release": "1.1", "date": "2014-11-11T15:42:01", "author": "n0255159"}]}
'''

__author__ = 'n0083510'

import ConfigParser
from datetime import datetime
import gc
import urllib2
import logging
import json
try:
    import pycurl
    pc = True
except ImportError:
    pc = False
import os
import StringIO
import sys
import tempfile
import time
from xml.sax import make_parser, handler
import zipfile

__author__ = 'n0255159'
__prog__ = 'Bing.py'
__release__ = '1.2'
__now__ = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

logging.basicConfig(format="%(asctime)s - %(name)s.%(funcName)s - %(levelname)s - %(message)s")


class ParseRequestID(handler.ContentHandler):
    """ No line feeds or leading space:
    <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
    <s:Header><h:TrackingId xmlns:h="https://bingads.microsoft.com/Reporting/v9">
    837ceec7-51d9-4cfa-890a-6c85e4e4508c</h:TrackingId></s:Header>
    <s:Body><SubmitGenerateReportResponse xmlns="https://bingads.microsoft.com/Reporting/v9">
    <ReportRequestId>1578536487</ReportRequestId></SubmitGenerateReportResponse>
    </s:Body></s:Envelope>"""

    logger = logging.getLogger("ParseRequestID")

    def __init__(self, namespace, debug=False):
        self.namespace = namespace
        self._content = False
        self._reqid = None
        if debug:
            self.logger.setLevel(logging.DEBUG)
        self.logger.debug("namespace = %s", self.namespace)

    def startElementNS(self, name, qname, attrs):
        self.logger.debug(name)
        if name[0] == self.namespace and name[1] == 'ReportRequestId':
            self._content = True
            self._reqid = ''

    def endElementNS(self, name, gname):
        self.logger.debug(name)
        if name[0] == self.namespace and name[1] == 'ReportRequestId':
            self._content = False

    def characters(self, content):
        if self._content:
            self._reqid += content

    def getRequestID(self):
        return self._reqid


class ParseCustomerInfo(handler.ContentHandler):
    """ No line feeds or leading space:
    <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Header>
    <h:TrackingId xmlns:h="https://bingads.microsoft.com/Customer/v9">
    866d4e17-eda4-4569-9aed-66d0b957274c</h:TrackingId></s:Header><s:Body>
    <GetCustomersInfoResponse xmlns="https://bingads.microsoft.com/Customer/v9">
    <CustomersInfo xmlns:a="https://bingads.microsoft.com/Customer/v9/Entities"
     xmlns:i="http://www.w3.org/2001/XMLSchema-instance"><a:CustomerInfo>
     <a:Id>21026476</a:Id><a:Name>test_liberty1</a:Name></a:CustomerInfo>
     </CustomersInfo></GetCustomersInfoResponse></s:Body></s:Envelope>"""

    logger = logging.getLogger("ParseCustomerInfo")

    def __init__(self, namespace, debug=False):
        self.namespace = namespace
        self._custinf = []
        self._key = None
        if debug:
            self.logger.setLevel(logging.DEBUG)
        self.logger.debug("namespace = %s", self.namespace)

    def startElementNS(self, name, qname, attrs):
        self.logger.debug(name)
        if name[0] == self.namespace:
            if name[1] == 'CustomerInfo':
                self._custinf.append({})
            elif name[1] in ('Id', 'Name'):
                self._key = name[1]
                self._custinf[-1][self._key] = ''
            else:
                self._key = None

    def endElementNS(self, name, gname):
        self.logger.debug(name)
        if name[0] == self.namespace and name[1] == 'CustomerInfo':
            self._key = None

    def characters(self, content):
        if self._key is not None:
            self._custinf[-1][self._key] += content

    def getCustomerInfo(self):
        return self._custinf


class ParseAccountInfo(handler.ContentHandler):
    """ No line feeds or leading space:
    <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Header>
    <h:TrackingId xmlns:h="https://bingads.microsoft.com/Customer/v9">
    bac212d2-09e3-4a1b-8181-63b8f582afeb</h:TrackingId></s:Header><s:Body>
    <GetAccountsInfoResponse xmlns="https://bingads.microsoft.com/Customer/v9">
    <AccountsInfo xmlns:a="https://bingads.microsoft.com/Customer/v9/Entities"
     xmlns:i="http://www.w3.org/2001/XMLSchema-instance"><a:AccountInfo><a:Id>
    8968241</a:Id><a:Name>test_liberty1</a:Name><a:Number>D000UPYG</a:Number>
    <a:AccountLifeCycleStatus>Pending</a:AccountLifeCycleStatus><a:PauseReason
     i:nil="true"/></a:AccountInfo></AccountsInfo></GetAccountsInfoResponse>
    </s:Body></s:Envelope>
    """

    logger = logging.getLogger("ParseAccountInfo")

    def __init__(self, namespace, debug=False):
        self.namespace = namespace
        self._accinf = []
        self._keys = False
        self._key = None
        if debug:
            self.logger.setLevel(logging.DEBUG)
        self.logger.debug("namespace = %s", self.namespace)

    def startElementNS(self, name, qname, attrs):
        self.logger.debug(name)
        if name[0] == self.namespace:
            if name[1] == 'AccountInfo':
                self._accinf.append({})
                self._keys = True
                return
            if self._keys:
                self._key = name[1]
                self._accinf[-1][self._key] = ''

    def endElementNS(self, name, gname):
        self.logger.debug(name)
        if name[0] == self.namespace and name[1] == 'AccountInfo':
            self._keys = False
            self._key = None

    def characters(self, content):
        if self._keys:
            self._accinf[-1][self._key] += content

    def getAccountInfo(self):
        return self._accinf


class ParseStatus(handler.ContentHandler):
    """ No line feeds or leading space:
    <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Header>
    <h:TrackingId xmlns:h="https://bingads.microsoft.com/Reporting/v9">
    863da5ca-4ca9-487c-996d-0fa7ae53b326</h:TrackingId></s:Header><s:Body>
    <PollGenerateReportResponse xmlns="https://bingads.microsoft.com/Reporting/v9">
    <ReportRequestStatus xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
    <ReportDownloadUrl>https://download.api.bingads.microsoft.com/ReportDownload
    /Download.aspx?q=LFLlSn9s8MbwVw5V03fWasWCeJgqeUotEJuHBp0wp%2f6U1GU3Eycu7zVYe
    9D1UnERh%2bD50lOVfoP9%2bKyS3KBkDy%2b0rDzDMkWeC%2f8yICvYDanJNBDn6t1cvZt98fJos
    Tkhuo2HYGFJaJzTLdhzJm97jiN%2fNClmNKuvLbypdvs8ju0q%2faAt4%2bUFPBem1BJ5%2baiNb
    hWJCgkI17hg6zO%2btH5iw%2bfalXURVu4GJnN1pjRpZn6Nl3M7onogEmlg9K195XN%2bDsy0Bnb
    wKqXyan5GOdJPqMu1SyWprZPf5KZTr0ucGzhnbsefBkahgAmYhiZDz2fXnRUfe%2b31eR1T9EGj4
    X1nRPo%3d</ReportDownloadUrl><Status>Success</Status></ReportRequestStatus>
    </PollGenerateReportResponse></s:Body></s:Envelope>"""

    logger = logging.getLogger("ParseStatus")

    def __init__(self, namespace, debug=False):
        self.namespace = namespace
        self._down = False
        self._download = None
        self._stat = False
        self._status = None
        if debug:
            self.logger.setLevel(logging.DEBUG)
        self.logger.debug("namespace = %s", self.namespace)

    def startElementNS(self, name, qname, attrs):
        self.logger.debug(name)
        if name[0] == self.namespace:
            if name[1] == 'Status':
                self._stat = True
                self._status = ''
            elif name[1] == 'ReportDownloadUrl':
                self._down = True
                self._download = ''

    def endElementNS(self, name, qname):
        self.logger.debug(name)
        if name[0] == self.namespace:
            if name[1] == 'Status':
                self._stat = False
            elif name[1] == 'ReportDownloadUrl':
                self._down = False

    def characters(self, content):
        self.logger.debug("_stat = %s, _down = %s", self._stat, self._down)
        if self._stat:
            self._status += content
        elif self._down:
            self._download += content

    def getDownloadURL(self):
        self.logger.debug(self._download)
        return self._download

    def getStatus(self):
        self.logger.debug(self._status)
        return self._status


class ParseData(handler.ContentHandler):
    # Errors and debugging.
    logger = logging.getLogger("ParseData")

    def __init__(self, columns, mapping, types, namespace, writer, formatter,
                 debug=False):
        self.columns = columns
        self.mapping = mapping
        self.types = types
        self.namespace = namespace
        self.writer = writer
        self.formatter = formatter
        if debug:
            self.logger.setLevel(logging.DEBUG)
        self._row = False
        self._data = {}

    def startElementNS(self, name, qname, attrs):
        self.logger.debug(name)
        # (namespace, localname) = name
        if name[0] == self.namespace and name[1] == 'Row':
            self._row = True
            return
        if self._row and name[0] == self.namespace:
            nam = self.mapping.get(name[1], name[1])
            if nam not in self.columns:
                return
            typ = self.types.get(nam, 's')
            val = attrs.getValueByQName('value')
            if typ == 'i':
                try:
                    self._data[nam] = int(val)
                except ValueError:
                    self.logger.error("failed converting '%s' to int for %r",
                                      val, nam)
            elif typ == 'f':
                try:
                    self._data[nam] = float(val)
                except ValueError:
                    if u'AveragePosition' != nam: # Bing often enough has no data for this one field.
                        self.logger.error("failed converting '%s' to float for %r",
                                          val, nam)
            else:
                self._data[nam] = val

    def endElementNS(self, name, qname):
        if name[0] == self.namespace and name[1] == 'Row':
            self._row = False
            if self._data:
                self.writer(self.formatter(self._data))
                self._data.clear()


class Bing(object):
    """
    Extract data from the Bing Ad API server.
    """

    soapHeader = """<?xml version="1.0" encoding="utf-8"?>
<soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
  <soapenv:Header xmlns="%s">
    <CustomerAccountId>%s</CustomerAccountId>
    <CustomerId>%s</CustomerId>
    <UserName>%s</UserName>
    <Password>%s</Password>
    <DeveloperToken>%s</DeveloperToken>
  </soapenv:Header>
  <soapenv:Body>"""
    soapFooter = "  </soapenv:Body>\n</soapenv:Envelope>\n"

    # Bing customer query template.
    soapCustomer = """
    <GetCustomersInfoRequest xmlns="%s">
      <CustomerNameFilter>%s</CustomerNameFilter>
      <TopN>%s</TopN>
      <ApplicationScope>%s</ApplicationScope>
    </GetCustomersInfoRequest>
"""

    # Bing account query template.
    soapAccount = """
    <GetAccountsInfoRequest xmlns="%s">
      <CustomerId>%s</CustomerId>
      <OnlyParentAccounts>%s</OnlyParentAccounts>
    </GetAccountsInfoRequest>
"""

    # http://msdn.microsoft.com/en-US/library/bing-ads-reporting-keywordperformancereportcolumn.aspx
    keywordReportColumns = ["TimePeriod",
                            "AccountName",
                            "CampaignName",
                            "Keyword",
                            "CurrentMaxCpc",
                            "QualityScore",
                            "Impressions",
                            "Clicks",
                            "Spend",
                            "AveragePosition",
                            "AdGroupStatus",
                            "BidMatchType",
                            "CampaignStatus",
                            "DestinationUrl",
                            "DeviceType",
                            "Network",
                            ]
    keywordReportMap = {"GregorianDate": 'TimePeriod',
                        "BiddedMatchType": 'BidMatchType',
                        "Devicetype": 'DeviceType'}
    keywordReportTypes = {"CurrentMaxCpc": 'f',
                          "QualityScore": 'i',
                          "Impressions": 'i',
                          "Clicks": 'i',
                          "Spend": 'f',
                          "AveragePosition": 'f',
                          }
    # http://msdn.microsoft.com/en-US/library/bing-ads-reporting-geographicallocationreportcolumn.aspx
    geographyReportColumns = ["TimePeriod",
                              "AccountName",
                              "CampaignName",
                              "AdGroupName",
                              "AdDistribution",
                              "Country",
                              "State",
                              "MetroArea",
                              "City",
                              "Impressions",
                              "Clicks",
                              "Spend",
                              "AveragePosition",
                              "Conversions",
                              ]
    geographyReportMap = {"GregorianDate": 'TimePeriod',
                          "CountryOrRegion": 'Country'}
    geographyReportTypes = {"Impressions": 'i',
                            "Clicks": 'i',
                            "Spend": 'f',
                            "AveragePosition": 'f',
                            "Conversions": 'i',
                            }

    soapReportHeader = """
    <SubmitGenerateReportRequest xmlns="https://bingads.microsoft.com/Reporting/v9">
      <ReportRequest xsi:type="%s">
        <Format>Xml</Format>
        <ReturnOnlyCompleteData>false</ReturnOnlyCompleteData>
        <Aggregation>Daily</Aggregation>
        <Columns>
"""
    soapReportColumn = "          <%s>%s</%s>\n"
    soapReportFooter = """        </Columns>
        <Scope>
          <AccountIds xmlns:a="http://schemas.microsoft.com/2003/10/Serialization/Arrays">
            <a:long>%s</a:long>
          </AccountIds>
        </Scope>
        <Time>
          %s
        </Time>
      </ReportRequest>
    </SubmitGenerateReportRequest>
""" #  Yesterday
#        <Filter />
#          <DeviceType>Computer SmartPhone</DeviceType>
#        </Filter>
#            <Scope>
#              <Campaigns>
#                <CampaignReportScope>
#                  <ParentAccountId>%s</ParentAccountId>
#                  <CampaignId>%s</CampaignId>
#                </CampaignReportScope>
#              </Campaigns>
#            </Scope>

    soapPredefinedTime = "<PredefinedTime>%s</PredefinedTime>"
    soapCustomDateRange = """<CustomDateRangeEnd>%s\n          </CustomDateRangeEnd>
          <CustomDateRangeStart>%s\n          </CustomDateRangeStart>"""
    soapCustomDate = "\n            <Day>%d</Day>\n            <Month>%d</Month>\n            <Year>%d</Year>"

    soapPoll = """
    <PollGenerateReportRequest xmlns="https://bingads.microsoft.com/Reporting/v9">
      <ReportRequestId>%s</ReportRequestId>
    </PollGenerateReportRequest>
"""

    # If this is not set, we fail.
    host = None
    test_rep_host = "api.sandbox.bingads.microsoft.com"
    test_cust_host = "clientcenter.api.sandbox.bingads.microsoft.com"
    prod_rep_host = 'api.bingads.microsoft.com'
    prod_cust_host = "clientcenter.api.bingads.microsoft.com"
    cust_uri = "CustomerManagement/V9/CustomerManagementService.svc"
    rep_uri = 'Advertiser/Reporting/v9/ReportingService.svc'

    # The Bing namespace definitions.
    ns_customer = "https://bingads.microsoft.com/Customer/v9"
    ns_customer_ent = ns_customer + "/Entities"
    len_customer_ent = len(ns_customer_ent) + 2
    # The report namespace
    nsdataReport = "https://bingads.microsoft.com/Reporting/v9"
    ns_repdata = "http://adcenter.microsoft.com/advertiser/reporting/v5/XMLSchema"
    len_repdata = len(ns_repdata) + 2

    # Output ordering.
    outer = ['CustomerId']
    inner = [('Id', 'AccountId'),
             ('Number', 'Number'),
             ('Name', 'Name'),
             ('AccountLifeCycleStatus', 'Status'),
             ('PauseReason', 'Reason')]

    # Errors and debugging.
    logger = logging.getLogger("Bing")

    wait_minutes = 1
    form_line = None

    # Other command line options:
    prod = False
    keyword = False
    geography = False
    period = 'Yesterday'
    text = False
    debug = False
    verbose = False
    meta = True
    pycurl = False

    # Loaded from a configuration file.
    config = '/etc/LM/bing.ini'
    username = None
    password = None
    devtoken = None

    def __init__(self, **args):
        """
        @param args: use prod and/or debug as named parameters, if needed.
        @type args: dictionary
        """
        for key in args.iterkeys():
            if hasattr(self, key):
                setattr(self, key, args[key])
        if self.verbose:
            self.logger.setLevel(logging.INFO)
        if self.debug:
            self.logger.setLevel(logging.DEBUG)
        if pycurl and not pc:
            self.pycurl = False
            self.logger.warn("pycurl selected, but it failed to import.")
        dop = 'test'
        if self.prod:
            dop = 'prod'
        self.chost = getattr(self, "%s_cust_host" % (dop, ))
        self.rhost = getattr(self, "%s_rep_host" % (dop, ))
        self.cwsdl = "https://%s/Api/%s" % (self.chost, self.cust_uri) #?wsdl
        self.logger.debug("customer WSDL URL: %s", self.cwsdl)
        self.rwsdl = "https://%s/Api/%s" % (self.rhost, self.rep_uri)
        self.logger.debug("report WSDL URL: %s", self.rwsdl)
        assert (isinstance(self.period, tuple) and
                len(self.period) == 2 and
                isinstance(self.period[0], datetime) and
                isinstance(self.period[1], datetime)) or \
            self.period in ("Today", "Yesterday", "LastSevenDays", "ThisWeek",
                            "LastWeek", "LastFourWeeks", "ThisMonth",
                            "LastMonth", "LastThreeMonths","LastSixMonths",
                            "ThisYear", "LastYear")
            # one http://msdn.microsoft.com/en-US/library/bing-ads-reporting-reporttimeperiod.aspx
        if self.logger.isEnabledFor(logging.DEBUG):
            for key in dir(self):
                self.logger.debug("%s = %r" % (key, getattr(self, key)))
        cp = ConfigParser.SafeConfigParser()
        cp.read(self.config)
        for name in ('username', 'password', 'devtoken'):
            try:
                setattr(self, name, cp.get(dop, name))
            except ConfigParser.NoSectionError, err:
                self.logger.error(err)
                self.logger.error(self.config)
                sys.exit(1)

    def _getService(self, namespace, soapBody, action, custid, acctid, wsdl, host):
        """
        The actual HTTPS POST call to the Bing API server.

        @param soapBody: one of the class query templates, populated.
        @type soapBody: string
        @param action: value for the SOAPAction header
        @type action: string
        @return: ElementTree or None
        """
        soapStr = self.soapHeader % (namespace,
                                     acctid,
                                     custid,
                                     self.username,
                                     self.password,
                                     self.devtoken
                                     ) + \
            soapBody + self.soapFooter
        self.logger.debug("post = %s", wsdl)
        req = urllib2.Request(wsdl)
        req.add_header("Accept", "text/xml")
        req.add_header("Accept", "multipart/*");
        req.add_header("Content-type", "text/xml; charset=\"UTF-8\"")
        req.add_header("SOAPAction", action)
        req.add_header("HOST", host)
        req.add_data(soapStr)
        self.logger.debug("soapStr for %s: %s", action, soapStr)
        res = None
        try:
            service = urllib2.urlopen(req)
            res = service.read()
            service.close()
            self.logger.debug("res: %s", res)
            return res
        except urllib2.URLError, err:
            self.logger.error("%s failed", action)
            if self.logger.level > logging.DEBUG:
                self.logger.error("soapStr: %s", soapStr)
            if res is not None:
                self.logger.error("res: %s", res)
            self.logger.error("reason: %s", str(err.reason))
            if isinstance(err, urllib2.HTTPError):
                self.logger.error("code: %r", err.code)
        return None

    def getCustomersInfo(self):
        """
        Create a Web service client, add the headers, and then execute the
        getCustomersInfo method.
        @return: ElementTree or None
        """
        rval = None
        tries = 0
        while not rval and tries < 5:
            if tries > 0:
                time.sleep(30)
            rval = self._getService(self.ns_customer,
                                    self.soapCustomer % (self.ns_customer, "",
                                                         "100", "Advertiser"),
                                    "GetCustomersInfo", '', '',
                                    self.cwsdl, self.chost)
            tries += 1
        return rval

    def getAccountsInfo(self, customerId, onlyParentAccounts):
        """
        Create a Web service client, add the headers, and then execute the
        getAccountsInfo method.

        @param customerId: extracted from getCustomersInfo
        @type customerId: string
        @param onlyParentAccounts: for now, "true"
        @type onlyParentAccounts: boolean string
        @return: ElementTree or None
        """
        rval = None
        tries = 0
        while not rval and tries < 5:
            if tries > 0:
                time.sleep(30)
            rval = self._getService(self.ns_customer,
                                    self.soapAccount % (self.ns_customer,
                                                        customerId,
                                                        onlyParentAccounts),
                                    "GetAccountsInfo", customerId, '',
                                    self.cwsdl, self.chost)
            tries += 1
        return rval

    def submitGenerateReport(self, soapBody, customerId, acctId):
        """
        Send a request to generate a report.

        @param soapBody: the XML body containing the report request
        @type soapBody: string
        @return: ElementTree or None
        """
        return self._getService(self.nsdataReport, soapBody,
                                'SubmitGenerateReport', customerId, acctId,
                                self.rwsdl, self.rhost)

    def pollGenerateReport(self, reportId, customerId, acctId):
        """
        Run the request to determine if a report is available yet.
        
        @param reportId: ReportRequestId field value from submitGenerateReport
        @type reportId: string
        @return: ElementTree or None
        """
        return self._getService(self.nsdataReport, self.soapPoll % (reportId, ),
                                'PollGenerateReport', customerId, acctId,
                                self.rwsdl, self.rhost)

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
        for key in self.outer:
            if data.has_key(key):
                rval.append("%s: %s" % (key, data[key]))
        if data.has_key('accounts'):
            rval.append("Accounts:")
            for account in data['accounts']:
                tabs = "\t"
                for kv in self.inner:
                    if account.has_key(kv[0]):
                        rval.append("%s%s: %s" % (tabs, kv[1], account[kv[0]]))
                        tabs = "\t\t"
        else:
            for key, val in data.iteritems():
                rval.append("%s = %s" % (key, val))
        return "\n".join(rval)

    def _json(self, data):
        """
        Dump the input dictionary as a JSON object on a single line, or return
        an empty string if the input dictionary is empty.

        @param data: value(s) to format into a string
        @type data: dictionary
        @return: a newline ended string, or an empty string
        """
        if len(data) == 0:
            return ""
        if self.meta:
            data['meta_history'] = [{'prog': __prog__,
                                     'release': __release__,
                                     'author': __author__,
                                     'date': __now__},]
        return json.dumps(data) + "\n"

    def _setFormat(self):
        """
        Set self.form_line to the method to use to format output.
        """
        if self.text:
            self.output.write("UserName: %s\n" % (self.username))
            self.form_line = self._text
        else:
            self.form_line = self._json

    def _getTimePeriod(self):
        """
        Build the XML fragment for the report <time/>.

        @return: XML string
        """
        if isinstance(self.period, tuple):
            period = self.soapCustomDateRange % \
                (self.soapCustomDate % (self.period[1].day,
                                        self.period[1].month,
                                        self.period[1].year),
                 self.soapCustomDate % (self.period[0].day,
                                        self.period[0].month,
                                        self.period[0].year))
        else:
            period = self.soapPredefinedTime % self.period
        self.logger.debug("period = %s", period)
        return period

    def _getReportSOAP(self, request, column, columns, acctid):
        """
        Build the XML fragment containing a full SOAP report request.

        @param request: http://msdn.microsoft.com/en-US/library/bing-ads-reporting-report-types.aspx
        @type request: string
        @param column: The name of the column type in the report type
        @type column: string
        @param columns: list of columns to download
        @type columns: list or tuple
        @return: XML string
        """
        soap = [self.soapReportHeader % (request,), ]
        for entry in columns:
            soap.append(self.soapReportColumn % (column, entry, column))
        soap.append(self.soapReportFooter % (acctid, self._getTimePeriod()))
        return ''.join(soap)

    def parseRequestId(self, response):
        """
        Extract the ReportRequestId from the given XML.

        @param response: submitGenerateReport return value
        @type response: string
        @return: request ID
        @rtype: string
        """
        parser = make_parser()
        prid = ParseRequestID(self.nsdataReport)
        parser.setContentHandler(prid)
        parser.setFeature(handler.feature_namespaces, 1)
        parser.parse(StringIO.StringIO(response))
        rval = prid.getRequestID()
        self.logger.debug("RequestId: %s", rval)
        return rval

    def parseCustomerInfo(self, response):
        """
        Extract the CustomerInfo(s) from the given XML.

        @param response: submitGenerateReport return value
        @type response: string
        @return: request ID
        @rtype: string
        """
        parser = make_parser()
        prid = ParseCustomerInfo(self.ns_customer_ent)
        parser.setContentHandler(prid)
        parser.setFeature(handler.feature_namespaces, 1)
        parser.parse(StringIO.StringIO(response))
        rval = prid.getCustomerInfo()
        self.logger.debug("CustomerInfo: %s", rval)
        return rval

    def parseAccountInfo(self, response):
        """
        Extract the CustomerInfo(s) from the given XML.

        @param response: submitGenerateReport return value
        @type response: string
        @return: request ID
        @rtype: string
        """
        parser = make_parser()
        prid = ParseAccountInfo(self.ns_customer_ent)
        parser.setContentHandler(prid)
        parser.setFeature(handler.feature_namespaces, 1)
        parser.parse(StringIO.StringIO(response))
        rval = prid.getAccountInfo()
        self.logger.debug("AccountInfo: %s", rval)
        return rval

    def parseStatus(self, response):
        """
        
        @param response: pollGenerateReport return value
        @type response: string
        @rtype: ParseStatus instance
        """
        parser = make_parser()
        ps = ParseStatus(self.nsdataReport, debug=self.debug)
        parser.setContentHandler(ps)
        parser.setFeature(handler.feature_namespaces, 1)
        parser.parse(StringIO.StringIO(response))
        return ps

    def parseRows(self, infile, columns, mapping, types):
        """
        Extract data rows from XML, and write requested output format.

        @param infile: XML of Bing report data
        @type infile: File like object with read method
        @param columns: list of columns downloaded
        @type columns: list or tuple
        @param mapping: map XML columns to values in columns
        @type mapping: dictionary
        @param types: non-string data types: 'i' - int, 'f' - float
        @type types: dictionary
        """
        parser = make_parser()
        parser.setContentHandler(ParseData(columns, mapping, types,
                                           self.ns_repdata, self.output.write,
                                           self.form_line)) #, self.debug
        parser.setFeature(handler.feature_namespaces, 1)
        parser.parse(infile)

    def _getPyCurl(self, tf, url):
        self.logger.debug(url)
        try:
            curl = pycurl.Curl()
            curl.setopt(curl.URL, str(url))
            curl.setopt(curl.FOLLOWLOCATION, 1)
            curl.setopt(curl.MAXREDIRS, 5)
            curl.setopt(curl.CONNECTTIMEOUT, 30)
            curl.setopt(curl.TIMEOUT, 300)
            curl.setopt(curl.NOSIGNAL, 1)
            curl.setopt(curl.WRITEDATA, tf.file)
            curl.perform()
            curl.close()
            return True
        except Exception, err:
            self.logger.error(err)
        return False

    def _getLiburl(self, tf, url):
        results = urllib2.urlopen(url)
        tf.write(results.read())

    def _unzipFiles(self, zf, columns, mapping, types):
        for filename in zf.namelist():
            self.logger.debug("zip filename = %s", filename)
            xf = tempfile.NamedTemporaryFile(delete=False)
            infile = None
            try:
                infile = zf.open(filename)
                for dat in infile:
                    xf.write(dat)
                xf.close()
            finally:
                if infile is not None:
                    infile.close()
            gc.collect()
            self.parseRows(xf.name, columns, mapping, types)
            os.remove(xf.name)

    def getCustomerAccount(self):
        """
        Get every customer ID our login has, and every account ID under that ID.
        @return: yield customer ID and account ID
        @rtype: tuple
        """
        self.logger.debug("")
        for cust in self.getCustomerAccountData():
            accounts = len(cust['accounts'])
            self.logger.debug("%d accounts in %s", accounts, cust['CustomerId'])
            ii = 1
            for acct in cust['accounts']:
                self.logger.debug("yield %s, %s", cust['CustomerId'], acct['Id'])
                yield cust['CustomerId'], acct['Id'], ii, accounts
                ii += 1

    def getCustomerAccountData(self):
        """
        Get every customer ID our login has, and every account under that ID.
        @return: yield the data for one customer ID
        @rtype: dictionary
        """
        self.logger.debug("")
        #Process each entry returned by getCustomersInfo through getAccountsInfo.
        customersInfoResponse = self.getCustomersInfo()
        if customersInfoResponse is None:
            self.logger.debug("did not get data from self.getCustomersInfo()")
            raise RuntimeError()
        first = True
        cInfos = self.parseCustomerInfo(customersInfoResponse)
        self.logger.debug("%d cInfos", len(cInfos))
        data = {}
        for cInfo in cInfos:
            if first:
                first = False
            else: # Adds a newline separator for text output.
                self.output.write(self.format({}))
            data['CustomerId'] = cInfo['Id']
            accountsInfoResponse = self.getAccountsInfo(cInfo['Id'], "true")
            if accountsInfoResponse is not None:
                data['accounts'] = self.parseAccountInfo(accountsInfoResponse)
            else:
                data['accounts'] = []
            self.logger.debug("yield %r", data)
            yield data

    def dataReport(self, request, column, columns, mapping, types):
        """
        Submit a keyword or geography report request, and save results.

        @param request: One of the Bing Reporting API v9 report types
        @type request: string
        @param column: The name of the column type in the report type
        @type column: string
        @param columns: list of columns to download
        @type columns: list or tuple
        @param mapping: map XML columns to values in columns
        @type mapping: dictionary
        @param types: non-string data types: 'i' - int, 'f' - float
        @type types: dictionary
        """
        self.logger.debug("%s, %s,...", request, column)
        self._setFormat()

        for cust, acct, count, accounts in self.getCustomerAccount():
            if self.geography:
                self.logger.info("geography for %r\t%d of %d\tcustomer ID = %s\taccount ID = %s",
                                 self.period, count, accounts, cust, acct)
            else:
                self.logger.info("keyword for %r\t%d of %d\tcustomer ID = %s\taccount ID = %s",
                                 self.period, count, accounts, cust, acct)
            # Call SubmitGenerateReport to retrieve the ReportRequestId
            soap = self._getReportSOAP(request, column, columns, acct)
            response = self.submitGenerateReport(soap, cust, acct)
            if response is None:
                return
            reportRequestId = self.parseRequestId(response)

            while True:
                response = self.pollGenerateReport(reportRequestId, cust, acct)
                stat = self.parseStatus(response)
                status = stat.getStatus()
                if status == "Success":
                    url = stat.getDownloadURL()
                    tf = tempfile.NamedTemporaryFile(mode='wb', delete=False)
                    if self.pycurl:
                        if not self._getPyCurl(tf, url):
                            response = self.submitGenerateReport(soap, cust, acct)
                            if response is None:
                                return
                            reportRequestId = self.parseRequestId(response)
                            continue
                    else:
                        self._getLiburl(tf, url)
                    tf.close()
                    zf = None
                    try:
                        zf = zipfile.ZipFile(tf.name)
                        self._unzipFiles(zf, columns, mapping, types)
                    except zipfile.BadZipfile:
                        self.logger.setLevel(logging.DEBUG)
                        self.logger.warning("using %s as a plain file", tf.name)
                        zf = open(tf.name)
                        self.parseRows(zf.name, columns, mapping, types)
                        self.logger.setLevel(logging.WARN)
                        if self.verbose:
                            self.logger.setLevel(logging.INFO)
                        if self.debug:
                            self.logger.setLevel(logging.DEBUG)
                    finally:
                        if zf is not None:
                            zf.close()
                    os.remove(tf.name)
                if status != "Pending":
                    break
                # Wait a while before getting the status again.
                time.sleep(self.wait_minutes * 60)

    def customerReport(self):
        """
        Generate the demo customer report.

        @param output: Where to send output
        @type output: A file like object open for writing
        """
        self._setFormat()
        for cust in self.getCustomerAccountData():
            self.output.write(self.form_line(cust))

    def keywordReport(self):
        """
        Generate the keyword report.
        """
        self.dataReport('KeywordPerformanceReportRequest',
                        'KeywordPerformanceReportColumn',
                        self.keywordReportColumns, self.keywordReportMap,
                        self.keywordReportTypes)
        
    def geographyReport(self):
        """
        Generate the geography report.
        """
        self.dataReport('GeoLocationPerformanceReportRequest',
                        'GeoLocationPerformanceReportColumn',
                        self.geographyReportColumns, self.geographyReportMap,
                        self.geographyReportTypes)

    def run(self, output):
        """
        Save the output object, and run the requested report.

        @param output: where to write output
        @type output: open file like object with write method
        """
        self.output = output
        if self.keyword:
            self.keywordReport()
        elif self.geography:
            self.geographyReport()
        else:
            self.customerReport()


def getReportingPeriod(begin, end, week, month, year, last):
    """
    Build the period parameter for Bing.__init__().

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
    elif week or month or year:
        if last:
            rval = 'Last'
        else:
            rval = 'This'
        if week:
            rval += 'Week'
        elif month:
            rval += 'Month'
        else:
            rval += 'Year'
    else:
        rval = 'Yesterday'
    return rval

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog [options] [output_file]")
    parser.add_option('-c', '--config', action='store', dest='config', default=Bing.config,
                      help='ini configuration file to use, defaults to ' + Bing.config)
    parser.add_option('-z', '--no-meta', action='store_false', dest='meta',
                      default=True,
                      help='if set, do not add processing metadata to JSON')
    parser.add_option('-d', '--debug', action='store_true', dest='debug',
                      default=False, help='Output in-process data')
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose',
                      default=False, help='Output processing status')
    parser.add_option('-t', '--text', action='store_true', dest='text',
                      default=False, help='Output text rather than JSON')
    parser.add_option('-p', '--prod', action='store_true', dest='prod',
                      default=False, help='If set, get production data')
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
    parser.add_option('-y', '--year', action='store_true', dest='year',
                      default=False, help='(this|last) year')
    parser.add_option('-l', '--last', action='store_true', dest='last',
                      default=False, help='last (week|month|year) instead of this')
    parser.add_option('-u', '--pycurl', action='store_true', dest='pycurl',
                      default=False, help='Use the pycurl library instead of urllib2')
    (opts, args) = parser.parse_args()
    if len(args) > 1:
        parser.error("incorrect number of arguments")
    client = Bing(config=opts.config,
                  prod=opts.prod,
                  keyword=opts.keyword,
                  geography=opts.geog,
                  period=getReportingPeriod(opts.begin, opts.end, opts.week,
                                            opts.month, opts.year, opts.last),
                  text=opts.text,
                  pycurl=opts.pycurl,
                  meta=opts.meta,
                  debug=opts.debug,
                  verbose=opts.verbose)
    output = sys.stdout
    if len(args) == 1:
        output = open(args[0], 'w')
    client.run(output)
