#!/usr/bin/env python
from __future__ import with_statement
from google.appengine.api import files

import logging
import os
import urllib
import webapp2

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app

from genxmlif import GenXmlIfError
from minixsv import pyxsval

import jinja2
import os

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

def getFileContent(path):
    os_path = os.path.join(os.path.split(__file__)[0], path)
    s = file(os_path, 'r').read()
    #logging.info('-----------------s: '+s)
    return s

class MainHandler(webapp2.RequestHandler):
    def get(self):
        uploadHandlerUrl = blobstore.create_upload_url('/upload_handler')
        all_blobs = blobstore.BlobInfo.all()

        templateVals = {
            'url_upload_handler' : uploadHandlerUrl,
            'all_blobs' : all_blobs,
            'url_maplayer' : 'maplayer',
            'url_delete' : 'delete',
        }

        template = jinja_environment.get_template('/templates/uploadsite.html')
        self.response.out.write(template.render(templateVals))


class Delete(webapp2.RequestHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        blob_key = blob_info.key()
        blobstore.delete(blob_key)
        self.redirect('/')


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        self.redirect('/servefile/%s' % blob_info.key())

class Test(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self):
        logging.info('Debugging {')
        logging.info('Debugging }')

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        
        if not blobstore.get(resource):
            self.error(404)
            return
        
        blob_info = blobstore.BlobInfo.get(resource)
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

        # redirect back to the upload page
        #self.redirect('/')

        # display the gpxtrack on the maplayer
        self.redirect('/maplayer/'+str(blob_key))


def main():
    application = webapp2.WSGIApplication([
        ('/', MainHandler),
        ('/test', Test),
        ('/delete/([^/]+)?', Delete),
        ('/upload_handler', UploadHandler),
        ('/servefile/([^/]+)?', ServeHandler),
        ], debug=True)
    #run_wsgi_app(application)
    return application

if __name__ == '__main__':
    main()

app = main()
