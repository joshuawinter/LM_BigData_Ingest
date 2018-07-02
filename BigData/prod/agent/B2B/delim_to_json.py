#!/usr/bin/python
'''
Convert a delimited file (comma, tab, pipe, etc) into JSON, either using field
name in the first row of the input file, or provided on the command line, and
using non-string types for the fields as given on the command line.

Command line usage: python delim_to_json.py input_path

Created on Sep 26, 2014

@author: Alan Brenner <alan.brenner@teradata.com> or alan.brenner@libertymutual.com
'''

import csv
from datetime import datetime
import logging
import json
import sys

__author__ = 'n0255159'
__prog__ = 'delim_to_json.py'
__release__ = '1.1'
__now__ = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

logging.basicConfig() # Stops "No handlers could be found...." message.


class DelimitedToJSON(object):
    # Errors and debugging.
    logger = logging.getLogger("DelimittedToJSON")

    # Other command line options:
    debug = False
    meta = True
    delimiter = ','
    header = None
    types = {}

    keys = None

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
        if self.header:
            self.header = self.header.split(',')
        self.logger.debug("header = %r", self.header)
        if self.types:
            self.types = dict([ii.split(':') for ii in self.types.split(',')])
        self.logger.debug("types = %r", self.types)

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
            data['_history'] = [{'prog': __prog__,
                                 'rel': __release__,
                                 'auth': __author__,
                                 'date': __now__},]
        try:
            return json.dumps(data) + "\n"
        except UnicodeDecodeError:
            try:
                return json.dumps(data, encoding='Windows-1252') + "\n"
            except:
                return json.dumps(data, ensure_ascii=False) + "\n"
            

    def _getType(self, ii):
        """
        Get the data type character from self.types or return the default 's'.

        @return: i, f, b, or s
        """
        return self.types.get(self.header[ii], 's')

    def _getData(self, row):
        """
        Turn the given row into a dictionary.

        @param row: one 'line' returned by csvReader
        @type row: list or tuple
        @return: dictionary with keys from self.header and values from row
        """
        rval = {}
        rowlen = len(row)
        if self.cols != rowlen:
            if rowlen > 0:
                self.logger.error("columns (%d, %r) do not match row (%d, %r)",
                                  self.cols, self.header, rowlen, row)
            return rval
        for ii in range(self.cols):
            typ = self._getType(ii)
            if typ == 'i':
                try:
                    rval[self.header[ii]] = int(row[ii])
                except ValueError, err:
                    self.logger.error(err)
            elif typ == 'f':
                try:
                    # Handle US$ notation, which really should be just numbers.
                    rval[self.header[ii]] = float(row[ii].replace('$', '').replace(',', '').strip())
                except ValueError, err:
                    self.logger.error(err)
            elif typ == 'b':
                if row[ii].lower() in ('true', 'yes', '1'):
                    rval[self.header[ii]] = True
                else:
                    rval[self.header[ii]] = False
            else:
                rval[self.header[ii]] = row[ii]
        return rval

    def run(self, infile, outfile):
        """
        Parse the named input into JSON in the named output.

        @param infile: delimited file to read from
        @type infile: file like object with a read method
        @param outfile: where to send JSON
        @type outfile: file like object with a write method
        """
        csvReader = csv.reader(infile, delimiter=self.delimiter)
        if not self.header:
            self.header = csvReader.next()
            self.logger.debug("header = %r", self.header)
        self.cols = len(self.header)
        row = None
        # Do not catch error's here. Let python barf to STDERR, which should
        # be redirected to some place that Splunk can catch it and alert.
        for row in csvReader:
            outfile.write(self._json(self._getData(row)))


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog [options] input_file [output_file]")
    parser.add_option('-d', '--debug', action='store_true', dest='debug',
                      default=False, help='Output in-process data.')
    parser.add_option('-z', '--no-meta', action='store_true', dest='meta',
                      default=False,
                      help='if set, do not add processing metadata to JSON')
    parser.add_option('-c', '--comma', action='store_true', dest='comma',
                      default=False, help='comma delimited file (default)')
    parser.add_option('-p', '--pipe', action='store_true', dest='pipe',
                      default=False, help='pipe delimited file')
    parser.add_option('-t', '--tab', action='store_true', dest='tab',
                      default=False, help='tab delimited file')
    parser.add_option('-m', '--delim', action='store', dest='delim',
                      default=None, help='use given delimiter')
    parser.add_option('-r', '--header', action='store', dest='header',
                      default=None,
                      help='use comma separated names instead of first row')
    parser.add_option('-y', '--types', action='store', dest='types',
                      help='comma separate, colon delimited "field2:i,field7:f"')
    (opts, args) = parser.parse_args()
    if len(args) == 0 or len(args) > 2:
        parser.error("incorrect number of arguments")
    params = {'debug': opts.debug}
    params['delim'] = opts.delim
    if opts.tab:
        params['delim'] = '\t'
    if opts.pipe:
        params['delim'] = '|'
    if opts.comma:
        params['delim'] = ','
    if not params['delim']:
        params.pop('delim')
    if opts.header:
        params['header'] = opts.header
    if opts.types:
        params['types'] = opts.types
    if opts.meta:
        params['meta'] = False
    dtj = DelimitedToJSON(**params)
    csvoutput = sys.stdout
    if len(args) == 2:
        csvoutput = open(args[1], 'w')
    csvinput = None
    if args[0].endswith('.gz'):
        import gzip
        csvinput = gzip.open(args[0])
    elif args[0].endswith('.bz2'):
        import bz2
        csvinput = bz2.BZ2File(args[0])
    else:
        csvinput =  open(args[0], 'rb')
    if csvinput is not None:
        dtj.run(csvinput, csvoutput)
