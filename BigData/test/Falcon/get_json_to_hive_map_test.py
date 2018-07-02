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
import get_json_to_hive_map as get_json_to_hive_map


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
    expval1 = ''
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
    expval2 = '"mapping.Creative_ID" = "Creative ID",' \
        ' "mapping.Creative_Size" = "Creative Size",' \
        ' "mapping.Creative_Pixel_Size" = "Creative Pixel Size",' \
        ' "mapping.Creative_Concept" = "Creative Concept",' \
        ' "mapping.Creative_Bucketing" = "Creative Bucketing",' \
        ' "mapping.Creative_Type" = "Creative Type",' \
        ' "mapping.Creative_Field_1" = "Creative Field 1",' \
        ' "mapping.Site_DFA" = "Site (DFA)",' \
        ' "mapping.Site_ID_DFA" = "Site ID (DFA)",' \
        ' "mapping.DRC_NB_INET_Assist_Gross_Produ" = "DRC_NB_INET_Assist_Gross_Produced",' \
        ' "mapping.DRC_INET_Gross_Policy_Premium_" = "DRC_INET_Gross_Policy_Premium_Amount",' \
        ' "mapping.INET_Gross_Policy_Premium_Amou" = "INET_Gross_Policy_Premium_Amount",' \
        ' "mapping.Field_NB_INET_Assist_Gross_Pro" = "Field_NB_INET_Assist_Gross_Produced",' \
        ' "mapping.Field_INET_Gross_Policy_Premiu" = "Field_INET_Gross_Policy_Premium_Amount",' \
        ' "mapping.OMN_Visits" = "OMN - Visits",' \
        ' "mapping.OMN_Quote_Starts" = "OMN - Quote Starts",' \
        ' "mapping.OMN_Proposal_Quote_Starts" = "OMN - Proposal Quote Starts",' \
        ' "mapping.OMN_Quote_Completes" = "OMN - Quote Completes",' \
        ' "mapping.Bind_Complete_CONDO_View_throu" = "Application : Bind Complete - CONDO: View-through Conversions",' \
        ' "mapping.Bind_Complete_CONDO_Click_thro" = "Application : Bind Complete - CONDO: Click-through Conversions"'
    expval3 = '"mapping.Creative_ID" = "Creative ID",' \
        ' "mapping.Creative_Size" = "Creative Size",' \
        ' "mapping.Creative_Pixel_Size" = "Creative Pixel Size",' \
        ' "mapping.Creative_Concept" = "Creative Concept",' \
        ' "mapping.Creative_Bucketing" = "Creative Bucketing",' \
        ' "mapping.Creative_Type" = "Creative Type",' \
        ' "mapping.creative_field_1" = "Creative Field 1",' \
        ' "mapping.Site_DFA" = "Site (DFA)",' \
        ' "mapping.Site_ID_DFA" = "Site ID (DFA)",' \
        ' "mapping.drc_nb_inet_assist_grss_prdcd" = "DRC_NB_INET_Assist_Gross_Produced",' \
        ' "mapping.drc_inet_grss_pol_prem_amt" = "DRC_INET_Gross_Policy_Premium_Amount",' \
        ' "mapping.inet_nb_gross_produced" = "INET_NB_Gross_Produced",' \
        ' "mapping.INET_Gross_Policy_Premium_Amou" = "INET_Gross_Policy_Premium_Amount",' \
        ' "mapping.Field_NB_INET_Assist_Gross_Pro" = "Field_NB_INET_Assist_Gross_Produced",' \
        ' "mapping.Field_INET_Gross_Policy_Premiu" = "Field_INET_Gross_Policy_Premium_Amount",' \
        ' "mapping.OMN_Visits" = "OMN - Visits",' \
        ' "mapping.OMN_Quote_Starts" = "OMN - Quote Starts",' \
        ' "mapping.OMN_Proposal_Quote_Starts" = "OMN - Proposal Quote Starts",' \
        ' "mapping.omn_quote_completes" = "OMN - Quote Completes",' \
        ' "mapping.bnd_cmplt_condo_vw_thru_cnvrsn" = "Application : Bind Complete - CONDO: View-through Conversions",' \
        ' "mapping.bnd_cmplt_condo_clk_thru_cnvsn" = "Application : Bind Complete - CONDO: Click-through Conversions"'

    def test_empty(self):
        gjn = get_json_to_hive_map.GetJsonToHiveMap()
        rval = gjn.run("")
        self.assertEqual("", rval)

    def test_string(self):
        gjn = get_json_to_hive_map.GetJsonToHiveMap()
        rval = gjn.run("Creative STRING")
        self.assertEqual("", rval)

    def test_int(self):
        gjn = get_json_to_hive_map.GetJsonToHiveMap()
        rval = gjn.run("Creative STRING -- INT")
        self.assertEqual("", rval)

    def test_simple(self):
        gjn = get_json_to_hive_map.GetJsonToHiveMap()
        rval = gjn.run(self.testdata1)
        self.assertEqual(self.expval1, rval)

    def test_complex(self):
        gjn = get_json_to_hive_map.GetJsonToHiveMap()
        rval = gjn.run(self.testdata2)
        self.assertEqual(self.expval2, rval)

    def test_csv_map(self):
        txt = os.path.join(os.path.dirname(sys.modules[__name__].__file__),
                           'test_map_csv.txt')
        gjn = get_json_to_hive_map.GetJsonToHiveMap(mapfile=txt)
        rval = gjn.run(self.testdata2)
        self.assertEqual(self.expval3, rval)

    def test_tsv_map(self):
        txt = os.path.join(os.path.dirname(sys.modules[__name__].__file__),
                           'test_map_tsv.txt')
        gjn = get_json_to_hive_map.GetJsonToHiveMap(mapfile=txt, tab=True)
        rval = gjn.run(self.testdata2)
        self.assertEqual(self.expval3, rval)

if __name__ == "__main__":
    unittest.main()
