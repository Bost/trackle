#!/usr/bin/env python
#
from __future__ import with_statement
from google.appengine.api import files

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
    #self.redirect('/serve/%s' % blob_info.key())
    self.redirect('/gps')

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

    filename = '/gs/data/my_file'
    wFileName = files.gs.create(filename, mime_type='application/octet-stream', acl='public-read')

    with files.open(wFileName, 'a') as f:
        f.write(sData)

    files.finalize(wFileName)

    self.response.out.write(sData)

def main():
    return webapp2.WSGIApplication([
        ('/', MainHandler),
        ('/upload', UploadHandler),
        #('/track/([^/]+)?', Track),
        ('/serve/([^/]+)?', ServeHandler),
        ], debug=True)
    #run_wsgi_app(application)

if __name__ == '__main__':
  main()

app = main()
