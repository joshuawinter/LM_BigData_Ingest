#!/usr/bin/env python2.6
'''
PYTHONPATH=src python test/API/Bing_test.py

Created on Jul 23, 2014

@author: Alan Brenner <alan.brenner@teradata.com> or <alan.brenner@libertymutual.com>
'''
from datetime import datetime
import os
import unittest
import sys
sys.path.append(os.path.join('..', '..', 'prod', 'edge', 'API'))
import Bing as Bing


class PassWrite(object):
    def write(self, *data):
        return "\t".join(data)

class Test(unittest.TestCase):
    reqid = """<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Header><h:TrackingId xmlns:h="https://bingads.microsoft.com/Reporting/v9">f06bc72d-525c-4c14-93ed-a01697e1074e</h:TrackingId></s:Header><s:Body><SubmitGenerateReportResponse xmlns="https://bingads.microsoft.com/Reporting/v9"><ReportRequestId>2505507448</ReportRequestId></SubmitGenerateReportResponse></s:Body></s:Envelope>"""
    poll1 = """<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Header><h:TrackingId xmlns:h="https://bingads.microsoft.com/Reporting/v9">c9ee8ccb-d13b-4e69-ac1b-47c4ed635d7d</h:TrackingId></s:Header><s:Body><PollGenerateReportResponse xmlns="https://bingads.microsoft.com/Reporting/v9"><ReportRequestStatus xmlns:i="http://www.w3.org/2001/XMLSchema-instance"><ReportDownloadUrl i:nil="true"/><Status>Pending</Status></ReportRequestStatus></PollGenerateReportResponse></s:Body></s:Envelope>"""
    dlurl = "https://download.api.si.bingads.microsoft.com/ReportDownload/Download.aspx?q=AqH1dSZsRDdWju8xJ8QrkrXDxVl1mF1au10lTQ5myHYX8uww5i%2bN2q5yEtaHFZijdGazVihtaFqRE3V83HX9BchXCsqvHvExbyRxwy6zEpqQnpxxfaMbpFKzEWoPlUvBbFjIwsfN%2b%2bGxtUAKNptp4YOIIsLkhRBeJ9Lv%2bYntWTrRQDLtd4BEglX8rwp6irU2zwpxo7%2fi75VxOGdp62DjySlgSNIwG5Zh12QxG3lXpQehu8gyIP1%2bhMjha9Cz83e%2f%2bwGnwlciJF2ai8pTzhUuuKqxj0WfdkysKpSnvGSUD9U60l%2bnHKLfqiNoTPVz%2bAp6wOvg3PP0996i41fvIbmdTgk%3d"
    poll2 = """<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Header><h:TrackingId xmlns:h="https://bingads.microsoft.com/Reporting/v9">b576d317-8d10-4c2f-a9e5-21ae755a80ae</h:TrackingId></s:Header><s:Body><PollGenerateReportResponse xmlns="https://bingads.microsoft.com/Reporting/v9"><ReportRequestStatus xmlns:i="http://www.w3.org/2001/XMLSchema-instance"><ReportDownloadUrl>%s</ReportDownloadUrl><Status>Success</Status></ReportRequestStatus></PollGenerateReportResponse></s:Body></s:Envelope>""" % dlurl

    def test_getReportingPeriod(self):
        rval = Bing.getReportingPeriod(None, None, False, False, False, False)
        self.assertEqual(rval, 'Yesterday')
        rval = Bing.getReportingPeriod('2014-07-22', None, False, False, False, False)
        self.assertEqual(rval, 'Yesterday')
        rval = Bing.getReportingPeriod(None, '2014-07-23', False, False, False, False)
        self.assertEqual(rval, 'Yesterday')
        self.assertRaises(ValueError, Bing.getReportingPeriod, '14-07-22',
                          '14-07-22', False, False, False, False)
        rval = Bing.getReportingPeriod('2014-07-22', '2014-07-23', False, False, False, False)
        begin = datetime.strptime('2014-07-22', '%Y-%m-%d')
        end = datetime.strptime('2014-07-23', '%Y-%m-%d')
        self.assertEqual(rval, (begin, end))
        rval = Bing.getReportingPeriod(None, None, True, False, False, False)
        self.assertEqual(rval, 'ThisWeek')
        rval = Bing.getReportingPeriod(None, None, False, True, False, False)
        self.assertEqual(rval, 'ThisMonth')
        rval = Bing.getReportingPeriod(None, None, False, False, True, False)
        self.assertEqual(rval, 'ThisYear')
        rval = Bing.getReportingPeriod(None, None, True, False, False, True)
        self.assertEqual(rval, 'LastWeek')
        rval = Bing.getReportingPeriod(None, None, False, True, False, True)
        self.assertEqual(rval, 'LastMonth')
        rval = Bing.getReportingPeriod(None, None, False, False, True, True)
        self.assertEqual(rval, 'LastYear')

    def test_init(self):
        bing = Bing.Bing()
        dev = 'https://clientcenter.api.sandbox.bingads.microsoft.com/' \
            'Api/CustomerManagement/V9/CustomerManagementService.svc'
        self.assertEqual(dev, bing.cwsdl)
        bing = Bing.Bing(prod=True)
        prod = 'https://clientcenter.api.bingads.microsoft.com/' \
            'Api/CustomerManagement/V9/CustomerManagementService.svc'
        self.assertEqual(prod, bing.cwsdl)
        bing = Bing.Bing(period='LastMonth')
        self.assertEqual("LastMonth", bing.period)
        begin = datetime.utcnow()
        end = datetime.today()
        bing = Bing.Bing(period=(begin, end))
        self.assertTrue(isinstance(bing.period, tuple))
        self.assertEqual(2, len(bing.period))
        self.assertEqual(begin, bing.period[0])
        self.assertRaises(AssertionError, Bing.Bing, period="Now")

    def test_text(self):
        bing = Bing.Bing()
        rval = bing._text({})
        self.assertEqual("\n", rval)
        rval = bing._text({"a": 1, "b": "c"})
        self.assertEqual('a = 1\nb = c', rval)

    def test_json(self):
        # Without meta=False, the second result will include a date dependent
        # value in the meta_history field, which is meta-data not data.
        bing = Bing.Bing(meta=False)
        rval = bing._json({})
        self.assertEqual("", rval)
        rval = bing._json({"a": 1, "b": "c"})
        self.assertEqual('{"a": 1, "b": "c"}\n', rval)

    def test_setFormat(self):
        bing = Bing.Bing()
        bing.output = PassWrite()
        bing._setFormat()
        self.assertEqual(bing._json, bing.form_line)
        bing.text = True
        bing._setFormat()
        self.assertEqual(bing._text, bing.form_line)

    def test_getTimePeriod(self):
        bing = Bing.Bing()
        rval = bing._getTimePeriod()
        self.assertEqual("<PredefinedTime>Yesterday</PredefinedTime>", rval)
        bing.period = "ThisWeek"
        rval = bing._getTimePeriod()
        self.assertEqual("<PredefinedTime>ThisWeek</PredefinedTime>", rval)
        begin = datetime.utcnow()
        end = datetime.today()
        bing.period = (begin, end)
        rval = bing._getTimePeriod()
        trgt = """<CustomDateRangeEnd>
            <Day>%d</Day>
            <Month>%d</Month>
            <Year>%d</Year>
          </CustomDateRangeEnd>
          <CustomDateRangeStart>
            <Day>%d</Day>
            <Month>%d</Month>
            <Year>%d</Year>
          </CustomDateRangeStart>""" % (end.day, end.month, end.year,
                                        begin.day,begin.month, begin.year)
        self.assertEqual(trgt, rval)

    def test_getReportSOAP(self):
        bing = Bing.Bing()
        rval = bing._getReportSOAP('TestRequest', 'TestColumn', ["TimePeriod",], '735123')
        expt = """
    <SubmitGenerateReportRequest xmlns="https://bingads.microsoft.com/Reporting/v9">
      <ReportRequest xsi:type="TestRequest">
        <Format>Xml</Format>
        <ReturnOnlyCompleteData>false</ReturnOnlyCompleteData>
        <Aggregation>Daily</Aggregation>
        <Columns>
          <TestColumn>TimePeriod</TestColumn>
        </Columns>
        <Scope>
          <AccountIds xmlns:a="http://schemas.microsoft.com/2003/10/Serialization/Arrays">
            <a:long>735123</a:long>
          </AccountIds>
        </Scope>
        <Time>
          <PredefinedTime>Yesterday</PredefinedTime>
        </Time>
      </ReportRequest>
    </SubmitGenerateReportRequest>
"""
        self.assertEqual(expt, rval)

    def test_parseRequestId(self):
        bing = Bing.Bing()
        rval = bing.parseRequestId(self.reqid)
        self.assertEqual("2505507448", rval)

    def _getCustomerInfo(self):
        pass

    def _getAccountsInfo(self):
        pass

    def test_parseStatus(self):
        bing = Bing.Bing()
        rval = bing.parseStatus(self.poll1)
        self.assertEqual("Pending", rval.getStatus())
        rval = bing.parseStatus(self.poll2)
        self.assertEqual("Success", rval.getStatus())

    def _parseRows(self):
        pass

    def test_getDownloadURL(self):
        bing = Bing.Bing()
        stat = bing.parseStatus(self.poll2)
        rval = stat.getDownloadURL()
        self.assertEqual(self.dlurl, rval)


if __name__ == "__main__":
    unittest.main()
