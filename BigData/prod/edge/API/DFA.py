#!/usr/bin/env python2.6
'''
This application expects the user name, password, and
developer token to be provided in the source below.

Command line usage: python DFA.py

Created on Oct 24, 2014

 openssl pkcs12  -nocerts -in DFA.p12 -out DFA.pem
banded-momentum-516

@author: n0255159 'Alan Brenner' <alan.brenner@teradata.com>
'''

from datetime import date, datetime, timedelta
import logging
import httplib2
import json
import sys

from apiclient.discovery import build
from oauth2client.client import SignedJwtAssertionCredentials, AccessTokenRefreshError

__author__ = 'n0255159'
__prog__ = 'DFA.py'
__release__ = '1.0'
__now__ = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

logging.basicConfig() # Stops "No handlers could be found...." message.


class DFA(object):
    """
    Fetch files from URL's like:
    https://console.developers.google.com/m/cloudstorage/b/dfa_-a13d19d76d559ce638a
        674393048b1a7d2441868/o/NetworkActivity_6096_2590334_11-16-2013.log.gz
    """

    # Errors and debugging.
    logger = logging.getLogger("DFA")

    base_url = "https://console.developers.google.com/m/cloudstorage/b/dfa_-a13d19d76d559ce638a674393048b1a7d2441868/o/"
    base_name = "NetworkActivity_6096_2590334_"
    base_ext = ".log.gz"
    date_pattern = "%m-%d-%Y"

    # Mimetype to use if one can't be guessed from the file extension.
    DEFAULT_MIMETYPE = 'application/octet-stream'

    # Email of the Service Account.
    SERVICE_ACCOUNT_EMAIL = '682807404883-prcstnrsuudr2k5dba2gp0cv3111p1l7@developer.gserviceaccount.com'

    # Path to the Service Account's Private Key file.
    SERVICE_ACCOUNT_PKCS12_FILE_PATH = './DFA.p12'

    # Other command line options:
    path = '/etc/LM/dfa.yaml'
    begin = None
    end = None
    text = False
    debug = False
    meta = True

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
        if self.begin is None:
            self.begin = date.today() - timedelta(days=1)
        if self.end is None:
            self.end = self.begin + timedelta(days=1)
        self.logger.debug("loading configuration from %s", self.path)


        f = file(self.SERVICE_ACCOUNT_PKCS12_FILE_PATH, 'rb')
        key = f.read()
        f.close()

        credentials = SignedJwtAssertionCredentials(self.SERVICE_ACCOUNT_EMAIL, key,
                                                    scope='https://www.googleapis.com/auth/drive')
        http = httplib2.Http()
        http = credentials.authorize(http)

        #self.drive = build('drive', 'v2', http=http)
        self.storage = build('storage', 'v1', http=http)


    def run(self, out):
        # Auto-iterate through all files that matches this query
        _BUCKET_NAME = 'dfa_-a13d19d76d559ce638a674393048b1a7d2441868'

        try:
            req = self.storage.buckets().get(bucket=_BUCKET_NAME)
            resp = req.execute()
            print json.dumps(resp, indent=2)

            fields_to_return = 'nextPageToken,items(name,size,contentType,metadata(my-key))'
            req = self.storage.objects().list(bucket=_BUCKET_NAME, fields=fields_to_return)
            # If you have too many items to list in one request, list_next() will
            # automatically handle paging with the pageToken.
            while req is not None:
                resp = req.execute()
                print json.dumps(resp, indent=2)
                req = self.storage.objects().list_next(req, resp)

        except AccessTokenRefreshError:
            print ("The credentials have been revoked or expired, please re-run"
                   "the application to re-authorize")

        #print self.drive
        #print dir(self.drive)
        #print "files"
        #files = self.drive.files()
        #flist = files.list()
        #print dir(flist)
        #data = flist.execute()
        #print len(data['items'])
        #for item in data['items']:
        #    print item.__class__
        #    for key in item.iterkeys():
        #        print key
        #        print item[key]
        #print flist.uri
        
        #print "children"
        #children = self.drive.children()
        #print children.list(folderId)
        #file_list = self.drive.files({'q': "'root' in parents"}).GetList()
        #for file1 in file_list:
        #    print 'title: %s, id: %s' % (file1['title'], file1['id'])

        #file3 = self.drive.CreateFile({'id': file2['id']})
        #print 'Downloading file %s from Google Drive' % file3['title'] # 'hello.png'
        #file3.GetContentFile('world.png')  # Save Drive file as a local file



if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog [options] [output_file]")
    parser.add_option('-d', '--debug', action='store_true', dest='debug',
                      default=False, help='Output in-process data.')
    parser.add_option('-z', '--no-meta', action='store_true', dest='meta',
                      default=False,
                      help='if set, do not add processing metadata to JSON')
    parser.add_option('-c', '--config', action='store', dest='config', default=DFA.path,
                      help='ini configuration file to use, defaults to ' + DFA.path)
    parser.add_option('-t', '--text', action='store_true', dest='text',
                      default=False, help='Output text rather than JSON')
    parser.add_option('-b', '--begin', dest='begin', default=None,
                      help='beginning date in ISO format YYYY-MM-DD')
    parser.add_option('-e', '--end', dest='end', default=None,
                      help='ending date in ISO format YYYY-MM-DD')
    (opts, args) = parser.parse_args()
    if len(args) > 1:
        parser.error("incorrect number of arguments")
    client = DFA(path=opts.config,
                 begin=opts.begin,
                 end=opts.end,
                 text=opts.text,
                 debug=opts.debug)
    out = None
    if len(args) == 1:
        if args[0] == '-':
            out = sys.stdout
        else:
            out = open(args[0], 'wb')
    client.run(out)

