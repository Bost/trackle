#!/usr/bin/env python
from __future__ import with_statement
from google.appengine.api import files

import logging
import os
import urllib

import webapp2
from google.appengine.ext import blobstore
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app

from genxmlif import GenXmlIfError
from minixsv import pyxsval

url = '/gps'

def getFileContent(path):
    os_path = os.path.join(os.path.split(__file__)[0], path)
    s = file(os_path, 'r').read()
    #logging.info('-----------------s: '+s)
    return s


class MainHandler(webapp.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/upload')
        self.response.out.write('<html><body>')
        self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
        self.response.out.write("""Upload gpx file: <input type="file" name="file"><br> <input type="submit"
            name="submit" value="Submit"> </form></body></html>""")


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        self.redirect('/serve/%s' % blob_info.key())

class Test(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self):
        logging.info('Debugging {')
        logging.info('Debugging }')

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        #self.send_blob(blob_info)

        blob_key = blob_info.key()
        #for b in blobstore.BlobInfo.all():
            #blob_key = b.key()
        blob_reader = blobstore.BlobReader(blob_key)

        inputText = blob_reader.read()
        
        # TODO The gpx.xsd cannot be placed in a subdirectory - why?
        xsdText = getFileContent('gpx.xsd')

        logging.info('XSD file read in')

        psviResult = ''
        try:
            # use default values of minixsv, location of the schema file must
            # be specified in the XML file
            #domTreeWrapper = pyxsval .parseAndValidate ("Test.xml") 

            # domTree is a minidom document object
            #domTree = domTreeWrapper.getTree()

            # call validator with non-default values
            psviResult = elementTreeWrapper = pyxsval.parseAndValidateString(
                inputText, xsdText,
                #xmlIfClass= pyxsval.XMLIF_ELEMENTTREE,
                #warningProc=pyxsval.PRINT_WARNINGS, 
                #errorLimit=200, verbose=1,
                #useCaching=0, processXInclude=0
                )

            # get elementtree object after validation
            #elemTree = elementTreeWrapper.getTree()

        except pyxsval.XsvalError, errstr:
            print errstr
            print "Validation aborted!"
 
        except GenXmlIfError, errstr:
            print errstr
            print "Parsing aborted!"

        logging.info('psviResult: '+str(psviResult))

        homeDir = '/gs/data'
        filename = homeDir+'/tmpfile'

        # listdir causes: raise ProtocolBufferEncodeError, "int32 too big"
        #ls = files.gs.listdir(homeDir)
        #logging.info('-----------ls: '+ls)

        #files.delete(filename)     # not needed, the file will be eventually overwritten

        fHandle = files.gs.create(
                filename,
                mime_type='application/octet-stream', acl='public-read')

        with files.open(fHandle, 'a') as f:
            f.write(inputText)

        files.finalize(fHandle)

        #self.response.out.write(inputText)
        self.redirect('/gps')



def main():
    application = webapp2.WSGIApplication([
        ('/', MainHandler),
        ('/test', Test),
        ('/upload', UploadHandler),
        ('/serve/([^/]+)?', ServeHandler),
        ], debug=True)
    #run_wsgi_app(application)
    return application

if __name__ == '__main__':
    main()

app = main()
