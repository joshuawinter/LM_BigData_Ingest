#!/usr/bin/python
'''
PYTHONPATH=src python test/B2B/delim_to_json_test.py

Created on Sep 26, 2014

@author: Alan Brenner <alan.brenner@teradata.com> or <alan.brenner@libertymutual.com>
'''

import json
import os
import unittest
import StringIO
import sys
sys.path.append(os.path.join('..', '..', 'prod', 'agent', 'B2B'))
import delim_to_json as delim_to_json


class Test(unittest.TestCase):
    def test_json(self):
        # Without meta=False, the second result will include a date dependent
        # value in the meta_history field, which is meta-data not data.
        dtj = delim_to_json.DelimitedToJSON(meta=False)

        rval = dtj._json({})
        self.assertEqual("", rval)

        rval = dtj._json({"a": 1, "b": "c"})
        self.assertEqual('{"a": 1, "b": "c"}\n', rval)

    def test_getType(self):
        dtj = delim_to_json.DelimitedToJSON()
        self.assertRaises(TypeError, dtj._getType, 1)
        dtj.types = {'a': 's', 'b': 'i', 'c': 'f', 'd': 'b'}
        dtj.header = ['a', 'c', 'b', 'd', 'e']

        rval = dtj._getType(0)
        self.assertEqual('s', rval)

        rval = dtj._getType(1)
        self.assertEqual('f', rval)

        rval = dtj._getType(2)
        self.assertEqual('i', rval)

        rval = dtj._getType(3)
        self.assertEqual('b', rval)

        rval = dtj._getType(4)
        self.assertEqual('s', rval)

    def test_getData(self):
        dtj = delim_to_json.DelimitedToJSON()
        dtj.types = {'a': 's', 'b': 'i', 'c': 'f', 'd': 'b'}
        dtj.header = ['a', 'c', 'b', 'd', 'e']
        dtj.cols = len(dtj.header)

        rval = dtj._getData(())
        self.assertEqual(rval, {})

        rval = dtj._getData(('too', 'few'))
        self.assertEqual(rval, {})

        rval = dtj._getData(('a', '1.0', '1', 'False', 'too', 'much'))
        self.assertEqual(rval, {})

        rval = dtj._getData(('a', '1.0', '1', 'False', 'value'))
        self.assertEqual(rval, {'a': 'a', 'b': 1, 'c': 1.0,
                                'd': False, 'e': 'value'})

        rval = dtj._getData(('a', '1.0', 'one', 'True', 'value'))
        self.assertEqual(rval, {'a': 'a', 'c': 1.0,
                                'd': True, 'e': 'value'})

    def test_run(self):
        dtj = delim_to_json.DelimitedToJSON()
        dtj.types = {'a': 's', 'b': 'i', 'c': 'f', 'd': 'b'}
        dtj.header = ['a', 'c', 'b', 'd', 'e']
        infile = StringIO.StringIO('v1,1.0,2,False')
        outfile = StringIO.StringIO()
        dtj.run(infile, outfile)
        rval = outfile.getvalue()
        self.assertEqual(rval, '')
        infile.close()
        outfile.close()

        infile = StringIO.StringIO('v1,1.0,2,False,v2,v3')
        outfile = StringIO.StringIO()
        dtj.run(infile, outfile)
        rval = outfile.getvalue()
        self.assertEqual(rval, '')
        infile.close()
        outfile.close()

        infile = StringIO.StringIO('v1,1.0,2,False,v2')
        outfile = StringIO.StringIO()
        dtj.run(infile, outfile)
        rval = json.loads(outfile.getvalue())
        # Don't test this run-time dependent value.
        rval['_history'][0].pop('date')
        self.assertEqual(rval, {u"a": u"v1", u"b": 2, u"c": 1.0,
                                u"d": False, u"e": u"v2",
                                u'_history': [{u'auth': u'n0255159',
                                               u'prog': u'delim_to_json.py',
                                               u'rel': u'1.1'}]})
        infile.close()
        outfile.close()


if __name__ == "__main__":
    unittest.main()
