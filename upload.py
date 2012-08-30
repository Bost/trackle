import os
import urllib

import logging
import cgi
import webapp2

from google.appengine.ext import blobstore
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

class MainHandler(webapp.RequestHandler):
    def get(self):
        #upload_url = blobstore.create_upload_url('/uploadHandler')
        upload_url = '/gps'
        files = ""
        for b in blobstore.BlobInfo.all():
            files += "<li><a href=\"/serve/" + str(b.key()) + "\">" + str(b.filename) + "</a>"

        s = """
<html><body>
<form action="%s" method="GET" enctype="multipart/form-data">
    <div>
        Upload File:
        <input type="file" name="file">
    </div>
    <div><input type="submit" name="submit" value="Submit"></div>
    %s
</form>
</body></html>
""" % (upload_url, files)
        self.response.out.write(s)


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')
        blob_info = upload_files[0]
        #self.redirect('/upload')
        self.redirect('/gps')

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, blob_key):
        blob_key = str(urllib.unquote(blob_key))
        s = ""
        if not blobstore.get(blob_key):
            self.error(404)
        else:
            info = blobstore.BlobInfo.get(blob_key)
            s = str(blobstore.get(blob_key))
            self.send_blob(info, save_as=True)
        logging.info("===: "+s)

app = webapp2.WSGIApplication(
          [('/upload', MainHandler),
           ('/uploadHandler', UploadHandler),
           ('/serve/([^/]+)?', ServeHandler),
          ], debug=True)

