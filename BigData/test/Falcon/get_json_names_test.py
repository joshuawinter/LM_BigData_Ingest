#!/usr/bin/python
'''
PYTHONPATH=src python test/B2B/delim_to_json_test.py

Created on Sep 26, 2014

@author: Alan Brenner <alan.brenner@teradata.com> or <alan.brenner@libertymutual.com>
'''

import os
import unittest
import sys
sys.path.append(os.path.join('..', '..', 'prod', 'admin', 'falcon'))
import get_json_names as get_json_names


class Test(unittest.TestCase):
    testdata1 = "TrafficDate STRING, -- TIMESTAMP" \
        "            AdvAccountName STRING," \
        "            State STRING," \
        "            Impressions STRING, -- INT" \
        "            Clicks STRING, -- INT" \
        "            NetCost STRING, -- DOUBLE" \
        "            Calls STRING," \
        "            QualifiedCalls STRING," \
        "            CallNetRevenue STRING," \
        "            AutoConversion STRING," \
        "            HomeConversion STRING," \
        "            AvgCPC STRING -- DOUBLE"
    expval1 = "TrafficDate STRING," \
        " AdvAccountName STRING," \
        " State STRING," \
        " Impressions STRING," \
        " Clicks STRING," \
        " NetCost STRING," \
        " Calls STRING," \
        " QualifiedCalls STRING," \
        " CallNetRevenue STRING," \
        " AutoConversion STRING," \
        " HomeConversion STRING," \
        " AvgCPC STRING"
    testdata2 = "Creative    STRING," \
        "            Creative ID STRING," \
        "            Creative Size STRING," \
        "            Creative Pixel Size STRING," \
        "            Creative Concept STRING," \
        "            Creative Bucketing STRING," \
        "            Creative Type STRING," \
        "            Creative Field 1 STRING," \
        "            Site (DFA) STRING," \
        "            Site ID (DFA) STRING," \
        "            DRC_NB_INET_Assist_Gross_Produced STRING, -- INT" \
        "            DRC_INET_Gross_Policy_Premium_Amount STRING, -- INT" \
        "            INET_NB_Gross_Produced STRING, -- INT" \
        "            INET_Gross_Policy_Premium_Amount STRING, -- INT" \
        "            Field_NB_INET_Assist_Gross_Produced STRING, -- INT" \
        "            Field_INET_Gross_Policy_Premium_Amount STRING, -- INT" \
        "            OMN - Visits STRING, -- INT" \
        "            OMN - Quote Starts STRING, -- INT" \
        "            OMN - Proposal Quote Starts STRING, -- INT" \
        "            OMN - Quote Completes STRING, -- INT" \
        "            Application : Bind Complete - CONDO: View-through Conversions STRING," \
        "            Application : Bind Complete - CONDO: Click-through Conversions STRING -- INT"
    expval2 = "Creative STRING," \
        " Creative_ID STRING," \
        " Creative_Size STRING," \
        " Creative_Pixel_Size STRING," \
        " Creative_Concept STRING," \
        " Creative_Bucketing STRING," \
        " Creative_Type STRING," \
        " Creative_Field_1 STRING," \
        " Site_DFA STRING," \
        " Site_ID_DFA STRING," \
        " DRC_NB_INET_Assist_Gross_Produ STRING," \
        " DRC_INET_Gross_Policy_Premium_ STRING," \
        " INET_NB_Gross_Produced STRING," \
        " INET_Gross_Policy_Premium_Amou STRING," \
        " Field_NB_INET_Assist_Gross_Pro STRING," \
        " Field_INET_Gross_Policy_Premiu STRING," \
        " OMN_Visits STRING," \
        " OMN_Quote_Starts STRING," \
        " OMN_Proposal_Quote_Starts STRING," \
        " OMN_Quote_Completes STRING," \
        " Bind_Complete_CONDO_View_throu STRING," \
        " Bind_Complete_CONDO_Click_thro STRING"
    expval3 = 'Creative STRING,' \
        ' Creative_ID STRING,' \
        ' Creative_Size STRING,' \
        ' Creative_Pixel_Size STRING,' \
        ' Creative_Concept STRING,' \
        ' Creative_Bucketing STRING,' \
        ' Creative_Type STRING,' \
        ' creative_field_1 STRING,' \
        ' Site_DFA STRING,' \
        ' Site_ID_DFA STRING,' \
        ' drc_nb_inet_assist_grss_prdcd STRING,' \
        ' drc_inet_grss_pol_prem_amt STRING,' \
        ' inet_nb_gross_produced STRING,' \
        ' INET_Gross_Policy_Premium_Amou STRING,' \
        ' Field_NB_INET_Assist_Gross_Pro STRING,' \
        ' Field_INET_Gross_Policy_Premiu STRING,' \
        ' OMN_Visits STRING,' \
        ' OMN_Quote_Starts STRING,' \
        ' OMN_Proposal_Quote_Starts STRING,' \
        ' omn_quote_completes STRING,' \
        ' bnd_cmplt_condo_vw_thru_cnvrsn STRING,' \
        ' bnd_cmplt_condo_clk_thru_cnvsn STRING'

    def test_empty(self):
        gjn = get_json_names.GetJsonNames()
        rval = gjn.run("")
        self.assertEqual("", rval)

    def test_string(self):
        gjn = get_json_names.GetJsonNames()
        rval = gjn.run("Creative STRING")
        self.assertEqual("Creative STRING", rval)

    def test_int(self):
        gjn = get_json_names.GetJsonNames()
        rval = gjn.run("Creative STRING -- INT")
        self.assertEqual("Creative STRING", rval)

    def test_simple(self):
        gjn = get_json_names.GetJsonNames()
        rval = gjn.run(self.testdata1)
        self.assertEqual(self.expval1, rval)

    def test_complex(self):
        gjn = get_json_names.GetJsonNames()
        rval = gjn.run(self.testdata2)
        self.assertEqual(self.expval2, rval)

    def test_csv_map(self):
        txt = os.path.join(os.path.dirname(sys.modules[__name__].__file__),
                           'test_map_csv.txt')
        gjn = get_json_names.GetJsonNames(mapfile=txt)
        rval = gjn.run(self.testdata2)
        self.assertEqual(self.expval3, rval)

    def test_tsv_map(self):
        txt = os.path.join(os.path.dirname(sys.modules[__name__].__file__),
                           'test_map_tsv.txt')
        gjn = get_json_names.GetJsonNames(mapfile=txt, tab=True)
        rval = gjn.run(self.testdata2)
        self.assertEqual(self.expval3, rval)

if __name__ == "__main__":
    unittest.main()
