#!/usr/bin/env python2.6
'''
PYTHONPATH=src python test/API/Google_test.py

Created on Oct 15, 2014

@author: Alan Brenner <alan.brenner@teradata.com> or <alan.brenner@libertymutual.com>
'''
import os
import unittest
import sys
sys.path.append(os.path.join('..', '..', 'prod', 'edge', 'API'))
import Google as Google


class PassWrite(object):
    def write(self, *data):
        return "\t".join(data)

class Test(unittest.TestCase):
    def test_text(self):
        google = Google.Google()
        rval = google._text({})
        self.assertEqual("\n", rval)
        rval = google._text({"a": 1, "b": "c"})
        self.assertEqual('\n', rval)

    def test_json(self):
        # Without meta=False, the second result will include a date dependent
        # value in the meta_history field, which is meta-data not data.
        google = Google.Google(meta=False)
        rval = google._json({})
        self.assertEqual("", rval)
        rval = google._json({"a": 1, "b": "c"})
        self.assertEqual('{"a": 1, "b": "c"}\n', rval)

    def test_split_line(self):
        google = Google.Google()
        google.columns = google.keywordReportColumns
        google.colcount = len(google.keywordReportColumns)
        cols = ('c1', 'c2')
        typs = {'c2': 'i'}
        rval = google._split_line("a\t2", cols, typs)
        self.assertEqual({}, rval)
        dval = {}
        sval = []
        ii = 0
        for key in google.keywordReportColumns:
            if google.keywordReportTypes.has_key(key):
                if google.keywordReportTypes[key] == 'i':
                    dval[key] = ii
                elif google.keywordReportTypes[key] == 'm':
                    dval[key] = ii / 1000000.0
                else:
                    dval[key] = float(ii)
            else:
                dval[key] = str(ii)
            sval.append(str(ii))
            ii += 1
        rval = google._split_line("\t".join(sval), google.keywordReportColumns,
                                  google.keywordReportTypes)
        self.assertEqual(dval, rval)


if __name__ == "__main__":
    unittest.main()
