#!/usr/bin/python

"""
Turn:
OMN - Quote Completes STRING, -- INT Application : Bind Complete - CONDO: View-through Conversions STRING,
into:
OMN_Quote_Completes STRING, Bind_Complete_CONDO_View_thro STRING,

@author: Alan Brenner <alan.brenner@teradata.com>
"""

import csv
import logging
import re

logging.basicConfig() # Stops "No handlers could be found...." message.

class GetJsonToHiveMap():

    # Errors and debugging.
    logger = logging.getLogger("JsonNames")

    notgood = re.compile(r"[^A-Za-z0-9_]")
    toomany = re.compile(r"__+")
    namemap = {}

    def __init__(self, mapfile=None, tab=False, debug=False):
        if mapfile:
            delim = ','
            if tab:
                delim = '\t'
            csvinput = None
            if mapfile.endswith('.gz'):
                import gzip
                csvinput = gzip.open(mapfile)
            elif mapfile.endswith('.bz2'):
                import bz2
                csvinput = bz2.BZ2File(mapfile)
            else:
                csvinput =  open(mapfile, 'rb')
            csvReader = csv.reader(csvinput, delimiter=delim)
            for row in csvReader:
                try:
                    self.namemap[row[0]] = row[1]
                except IndexError, err:
                    self.logger.error(err)
                    self.logger.error(row)
        if debug:
            self.logger.setLevel(logging.DEBUG)
        self.logger.debug("map = %r", self.namemap)

    def remove_comments(self, parts):
        self.logger.debug("remove_comments(%r)", parts)
        rval = []
        for ii in range(len(parts)):
            pos = parts[ii].find(' -- ')
            if parts[ii].startswith(' -- '):
                self.logger.debug("found starting comment in '%s'", parts[ii])
                val = parts[ii][parts[ii][5:].index(' ') + 6:].rsplit(None, 1)[0].strip()
                self.logger.debug("saving '%s'", val)
                rval.append(val)
            elif pos > 1:
                self.logger.debug("found ending comment in '%s'", parts[ii])
                val = parts[ii][0:pos + 1].rsplit(None, 1)[0].strip()
                self.logger.debug("saving '%s'", val)
                rval.append(val)
            else:
                val = parts[ii].rsplit(None, 1)[0].strip()
                self.logger.debug("saving '%s'", val)
                rval.append(val)
        return rval

    def replace_characters(self, json_names):
        """
        Replace any non [A-Za-z0-9_] characters with an underscore.

        @param json_names: each entry is column name, space, space-less data type
        @type json_names: array of strings 
        @return: the names that need mapping, and the map targets
        @rtype: dictionary of strings
        """
        hive_names = {}
        self.logger.debug("replace_characters(%r)", json_names)
        for ii in range(len(json_names)):
            if self.namemap.has_key(json_names[ii]):
                hive_names[json_names[ii]] = self.namemap[json_names[ii]]
            elif self.notgood.search(json_names[ii]):
                self.logger.debug("not a good column name: '%s'", json_names[ii])
                val = re.sub(self.notgood, '_', json_names[ii])
                val = re.sub(self.toomany, '_', val)
                if val.endswith('_'):
                    val = val[0:-1]
                self.logger.debug("saving %s -> %s", json_names[ii], val)
                hive_names[json_names[ii]] = val
            elif len(json_names[ii]) > 30:
                self.logger.debug("saving long %s", json_names[ii])
                hive_names[json_names[ii]] = json_names[ii]
        return hive_names

    def shorten_names(self, hive_names):
        """
        SAS doesn't like column names longer than 30 characters.

        @param hive_names: each entry is column name, space, space-less data type
        @type hive_names: array of strings 
        @return: the input array, with any needed changes in-place
        @rtype: array of strings
        """
        self.logger.debug("shorten_names(%r)", hive_names)
        for key in hive_names.iterkeys():
            if len(hive_names[key]) > 30:
                self.logger.debug("shortening: '%s'", hive_names[key])
                if hive_names[key].startswith('Application_'):
                    val = hive_names[key][12:]
                else:
                    val = hive_names[key]
                if len(val) > 30:
                    val = val[0:30]
                self.logger.debug("saving %s -> %s", key, val)
                hive_names[key] = val
        return hive_names

    def run(self, args):
        """
        @param args: a line defining attributes expected in JSON objects
        @type args: string
        @return: valid hive column name mapping
        @rtype: string
        """
        rval = []
        parts = args.split(',')
        if len(parts) == 1 and len(parts[0]) == 0:
            return ""
        json_names = self.remove_comments(parts)
        hive_names = self.replace_characters(json_names)
        hive_names = self.shorten_names(hive_names)

        # This preserves order, which is helpful for unit testing.
        self.logger.debug(hive_names)
        for ii in range(len(json_names)):
            self.logger.debug(json_names[ii])
            if not hive_names.has_key(json_names[ii]):
                continue
            rval.append('"mapping.%s" = "%s"' % (hive_names[json_names[ii]], json_names[ii]))
        return ", ".join(rval)


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog [options] source_table target_table")
    parser.add_option('-d', '--debug', action='store_true', dest='debug',
                      default=False, help='Output in-process data')
    parser.add_option('-m', '--map', action='store', dest='mapfile',
                      default=None, help='Path to csv of JSON,Hive pairs')
    parser.add_option('-t', '--tab', action='store_true', dest='tab',
                      default=False, help='Map file is tab, not comma separated')
    (options, args) = parser.parse_args()
    jhm = GetJsonToHiveMap(mapfile=options.mapfile, tab=options.tab,
                           debug=options.debug)
    jhm.run(args[0])
