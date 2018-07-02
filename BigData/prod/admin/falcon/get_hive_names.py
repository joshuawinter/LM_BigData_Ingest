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

class GetHiveNames():

    # Errors and debugging.
    logger = logging.getLogger("GetHiveNames")

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

    def remove_comments_replace_types(self, parts):
        """
        Manage data types, including removing comments.
        """
        self.logger.debug("remove_comments_replace_types(%r)", parts)
        rval = []
        for ii in range(len(parts)):
            pos = parts[ii].find(' -- ')
            if parts[ii].startswith(' -- '):
                self.logger.debug("found starting comment in '%s'", parts[ii])
                dtyp = parts[ii][4:parts[ii][5:].index(' ') + 5]
                self.logger.debug("dtyp = '%s'", dtyp)
                prev = rval[ii - 1].rsplit(' ', 1)
                self.logger.debug(prev)
                val = "%s %s" % (prev[0], dtyp)
                self.logger.debug(val)
                rval[ii - 1] = val
                val = parts[ii][parts[ii][5:].index(' ') + 6:]
                rval.append(val.strip())
            elif pos > 1:
                self.logger.debug("found ending comment in '%s'", parts[ii])
                name = parts[ii][0:pos].strip()
                name = name[0:name.rfind(' ')].strip()
                self.logger.debug("name = %s", name)
                dtyp = parts[ii][pos + 4:].strip()
                self.logger.debug("dtyp = %s", dtyp)
                rval.append("%s %s" % (name, dtyp))
            else:
                self.logger.debug("saving '%s'", parts[ii])
                rval.append(parts[ii].strip())
        return rval

    def map_replacement(self, rval):
        """
        If we were given a json name -> hive name map, do the replacement.

        @param rval: each entry is column name, space, space-less data type
        @type rval: array of strings 
        @return: the input array, with any needed changes in-place
        @rtype: array of strings
        """
        self.logger.debug("map_replacement(%r)", rval)
        if self.namemap:
            for ii in range(len(rval)):
                parts = rval[ii].rsplit(None, 1)
                if self.namemap.has_key(parts[0]):
                    rval[ii] = "%s %s" % (self.namemap[parts[0]], parts[1])
        return rval

    def manage_timestamps(self, rval):
        self.logger.debug("manage_timestamps(%r)", rval)
        # Copy all values, not a top level reference copy.
        parts = rval[:]
        del rval[:]
        for ii in range(len(parts)):
            if parts[ii].endswith('TIMESTAMP'):
                name = parts[ii].rsplit(' ', 1)[0]
                rval.append("%s_ISO STRING" % (name, ))
                rval.append("%s_INT BIGINT" % (name, ))
            else:
                rval.append(parts[ii])
        return rval

    def replace_characters(self, rval):
        """
        Replace any non [A-Za-z0-9_] characters with an underscore.

        @param rval: each entry is column name, space, space-less data type
        @type rval: array of strings 
        @return: the input array, with any needed changes in-place
        @rtype: array of strings
        """
        self.logger.debug("replace_characters(%r), rval")
        for ii in range(len(rval)):
            parts = rval[ii].rsplit(None, 1)
            if len(parts) != 2:
                self.logger.error("no space for data type separator in '%s'", rval[ii])
                continue
            if self.notgood.search(parts[0]):
                self.logger.debug("not a good column name: '%s'", parts[0])
                val = re.sub(self.notgood, '_', parts[0])
                val = re.sub(self.toomany, '_', val)
                if val.endswith('_'):
                    val = val[0:-1]
                rval[ii] = "%s %s" % (val, parts[1])
            else:
                rval[ii] = "%s %s" % (parts[0].strip(), parts[1])
        return rval

    def shorten_names(self, rval):
        """
        SAS doesn't like column names longer than 30 characters.

        @param rval: each entry is column name, space, space-less data type
        @type rval: array of strings 
        @return: the input array, with any needed changes in-place
        @rtype: array of strings
        """
        self.logger.debug("shorten any long name")
        for ii in range(len(rval)):
            parts = rval[ii].rsplit(None, 1)
            if len(parts[0]) > 30:
                self.logger.debug("shortening: '%s'", parts[0])
                if parts[0].startswith('Application_'):
                    val = parts[0][12:]
                else:
                    val = parts[0]
                if len(val) > 30:
                    val = val[0:30]
                rval[ii] = "%s %s" % (val, parts[1])
        return rval

    def run(self, arg):
        """
        @param arg: a line defining attributes expected in JSON objects
        @type arg: string
        @return: valid hive column names
        @rtype: string
        """
        self.logger.debug("run(%r)", arg)
        parts = arg.split(',')
        if len(parts) == 1 and len(parts[0]) == 0:
            return ""
        rval = self.remove_comments_replace_types(parts)
        rval = self.map_replacement(rval)
        rval = self.manage_timestamps(rval)
        rval = self.replace_characters(rval)
        rval = self.shorten_names(rval)
        return ", ".join(rval)

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog [options] 'one long string'")
    parser.add_option('-d', '--debug', action='store_true', dest='debug',
                      default=False, help='Output in-process data')
    parser.add_option('-m', '--map', action='store', dest='mapfile',
                      default=None, help='Path to csv of JSON,Hive pairs')
    parser.add_option('-t', '--tab', action='store_true', dest='tab',
                      default=False, help='Map file is tab, not comma separated')
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("incorrect number of arguments")
    gjn = GetHiveNames(mapfile=options.mapfile, tab=options.tab, debug=options.debug)
    print gjn.run(args[0])
