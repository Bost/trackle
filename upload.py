#!/usr/bin/env python
#

import os
import urllib

import webapp2
from google.appengine.ext import blobstore
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app

class MainHandler(webapp.RequestHandler):
  def get(self):
    upload_url = blobstore.create_upload_url('/upload')
    self.response.out.write('<html><body>')
    self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
    self.response.out.write("""Upload File X: <input type="file" name="file"><br> <input type="submit"
        name="submit" value="Submit"> </form></body></html>""")

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
    blob_info = upload_files[0]
    self.redirect('/serve/%s' % blob_info.key())

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    resource = str(urllib.unquote(resource))
    blob_info = blobstore.BlobInfo.get(resource)

    blob_key = blob_info.key()
    #for b in blobstore.BlobInfo.all():
        #blob_key = b.key()
    blob_reader = blobstore.BlobReader(blob_key)

    value = blob_reader.read()
    sData = ""
    sData += value
    #self.send_blob(blob_info)
    self.response.out.write(sData)

def main():
  application = webapp.WSGIApplication(
    [('/', MainHandler),
     ('/upload', UploadHandler),
     ('/serve/([^/]+)?', ServeHandler),
    ], debug=True)
  run_wsgi_app(application)

if __name__ == '__main__':
  main()

app = webapp2.WSGIApplication(
      [
          ('/', MainHandler),
          ('/upload', UploadHandler),
          ('/serve/([^/]+)?', ServeHandler),
          ], debug=True)

#from __future__ import with_statement
#from google.appengine.api import files

#import os
#import urllib

#import logging
#import cgi
#import webapp2

#from google.appengine.ext import blobstore
#from google.appengine.ext import webapp
#from google.appengine.ext.webapp import blobstore_handlers
#from google.appengine.ext.webapp import template
#from google.appengine.ext.webapp.util import run_wsgi_app

#class MainHandler(webapp.RequestHandler):
    #def get(self):
        ##try:
            ##files.gs
        ##except AttributeError:
            ##import gs
            ##files.gs = gs

        ### Create a file
        ##filename = '/gs/data/my_file'
        
        ##params = {'date-created':'092011', 'owner':'Jon'}

        ##writable_file_name = files.gs.create(filename, mime_type='application/octet-stream', acl='public-read')

        ### Open and write the file.
        ##with files.open(writable_file_name, 'a') as f:
            ##f.write('Hello World!')
            ##f.write('This is my first Google Cloud Storage object!')
            ##f.write('How exciting!')

        ### Finalize the file.
        ##files.finalize(writable_file_name)

        ## Open and read the file.
        ##logging.info('Opening file: '+filename)
        ##sData = ""
        ##with files.open(filename, 'r') as f:
            ##data = f.read(1000)
            ##sData += data
            ##while data != "":
                ##sData += data
                ###print data
                ##data = f.read(1000)

        #sData = ""
        #upload_url = blobstore.create_upload_url('/uploadHandler')
        ##upload_url = '/gps'
        #myFiles = ""
        #for b in blobstore.BlobInfo.all():
            #blob_key = b.key()
            #fName = b.filename
            #myFiles += "<li><a href=\"/serve/" + str(blob_key) + "\">" + str(fName) + "</a>"

            #logging.info("fName: "+fName)
            ## Instantiate a BlobReader for a given Blobstore value.
            #blob_reader = blobstore.BlobReader(blob_key)

            ## Instantiate a BlobReader for a given Blobstore value, setting the
            ## buffer size to 1 MB.
            ##blob_reader = blobstore.BlobReader(blob_key, buffer_size=1048576)

            ## Instantiate a BlobReader for a given Blobstore value, setting the
            ## initial read position.
            ##blob_reader = blobstore.BlobReader(blob_key, position=4194304)

            ## Read the entire value into memory. This may take a while depending
            ## on the size of the value and the size of the read buffer, and is not
            ## recommended for large values.
            #value = blob_reader.read()
            #sData += value

        #s = """
#<html><body>
#<form action="%s" method="GET" enctype="multipart/form-data">
    #<div>
        #Upload File:
        #<input type="file" name="file">
    #</div>
    #<div><input type="submit" name="submit" value="Submit"></div>
    #%s
#</form>
#</body></html>
#<!--
#%s
#-->
#""" % (upload_url, myFiles, sData)
        #self.response.out.write(s)


#class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    #def post(self):
        #upload_files = self.get_uploads('file')
        #blob_info = upload_files[0]
        #self.redirect('/upload')
        ##self.redirect('/gps')

#class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    #def get(self, blob_key):
        #blob_key = str(urllib.unquote(blob_key))
        #s = ""
        #if not blobstore.get(blob_key):
            #self.error(404)
        #else:
            #info = blobstore.BlobInfo.get(blob_key)
            #s = str(blobstore.get(blob_key))
            #self.send_blob(info, save_as=True)
        #logging.info("===: "+s)

#app = webapp2.WSGIApplication([
    ##('/upload', MainHandler),
    #('/', MainHandler),
    #('/uploadHandler', UploadHandler),
    #('/serve/([^/]+)?', ServeHandler),
    #], debug=True)

