#!/usr/bin/env python
from __future__ import with_statement

import logging
import os
import urllib
import webapp2
import jinja2

from dateutil.relativedelta import *
from dateutil.parser import *
from datetime import *
import commands

from math import sqrt, cos, pi

from google.appengine.ext import blobstore
from google.appengine.ext import db
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app

from minixsv import pyxsval
from genxmlif import GenXmlIfError

doctype = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">'
meta_tag = '<meta http-equiv="Content-Type content="text/html;charset=ISO-8859-1" />'

vMaxElevation = 'vMaxElevation'
vMinElevation = 'vMinElevation'
vDistance = 'vDistance'
vDuration = 'vDuration'
vTimeStmpStart = 'vTimeStmpStart'
vTimeStmpStop = 'vTimeStmpStop'
vAllValues = 'vAllValues'

distanceUnits = 'km'
elevationUnits = 'm'
speedUnits = 'km / h'

# Earth radius in kilometer
R = 6371
undef = -1

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class TrackDetails():
    file_name = undef
    timestamp = undef
    location = undef
    avrg_speed = undef
    duration = undef
    distance = undef
    top_speed = undef
    total_ascending = undef
    total_descending = undef
    elevation_gain = undef
    elevation_max = undef
    elevation_min = undef

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
            'doctype' : doctype,
            'meta_tag' : meta_tag,
            'url_upload_handler' : uploadHandlerUrl,
            'all_blobs' : all_blobs,
            'url_maplayer' : 'maplayer',
            'url_delete' : 'delete',
            'url_download' : 'download',
            'url_details' : 'details',
        }
        template = jinja_environment.get_template('/templates/uploadsite.html')
        self.response.out.write(template.render(templateVals))


class Details(webapp2.RequestHandler):
    def deg2rad(self, degree):
        return (pi * float(degree) / 180.0)

    def getVal(self, blob_key, vType=1):
        blob_reader = blobstore.BlobReader(blob_key)
        inputText = blob_reader.read()

        elementTree = ''
        root = ''
        try:
            xsValidator = pyxsval.XsValidator ()
            elementTreeWrapper = xsValidator.parseString(inputText)

            elementTree = elementTreeWrapper.getTree()
            root = elementTreeWrapper.getRootNode()
        except GenXmlIfError, errstr:
            print errstr
            logging.error("Parsing aborted!")

        except db.Timeout, errstr:
            #except (db.Timeout, db.InternalError):
            #except datastore_errors.Timeout, errstr:
            print errstr
            logging.error('Timeout-specific error page')

        valStart = undef
        valStop = undef
        lon1 = undef
        lat1 = undef
        lon2 = undef
        lat2 = undef
        distance = 0

        elevations = []
        rootChildren = root.getChildren()
        i = 0
        for root_c in rootChildren:
            s = root_c.getTagName()
            #logging.info('---- : '+ s)
            if s == "trk":
                trkChildren = root_c.getChildren()
                for trk_c in trkChildren:
                    s = trk_c.getTagName()
                    #logging.info('---- ---- : '+ s)
                    if s == "trkseg":
                        trkseqChildren = trk_c.getChildren()
                        for trkseq_c in trkseqChildren:
                            #s = trkseq_c.getTagName()
                            #logging.info('---- ---- ---- : '+ s)
                            lon1 = lon2
                            lat1 = lat2

                            lon_degree = float(trkseq_c.getAttribute("lon"))
                            lon2 = self.deg2rad(lon_degree)
                            #logging.info('lon_degree : '+ str(lon_degree)+'; lon2: '+str(lon2))

                            lat_degree = float(trkseq_c.getAttribute("lat"))
                            lat2 = self.deg2rad(lat_degree)
                            #logging.info('lat_degree : '+ str(lat_degree)+'; lat2: '+str(lat2))

                            if (vType == vDistance or vType == vAllValues) and lon1 != undef and lat1 != undef:
                                x = (lon2-lon1) * cos((lat1+lat2)/2)
                                y = (lat2-lat1)
                                d = sqrt(x*x + y*y) * R
                                #logging.info('i:'+str(i)+'; d: '+str(d))
                                #i += 1
                                distance += d

                            #logging.info('---- ---- ---- : '+ 'lon :'+lon + ' lat: '+lat)
                            trkptChildren = trkseq_c.getChildren()
                            for trkpt_c in trkptChildren:
                                s = trkpt_c.getTagName()
                                #logging.info('---- ---- ---- ---- : '+ s)
                                if s == "ele":
                                    ele_v = trkpt_c.getElementValue()
                                    #logging.info('---- ---- ---- ---- : '+ str(ele_v))
                                    elevations.append(ele_v)
                                if s == "time":
                                    if (vType == vDuration or vType == vAllValues):
                                        time_v = trkpt_c.getElementValue()
                                        if valStart == undef:
                                            valStart = time_v
                                        else:
                                            valStop = time_v

        trackDetails = TrackDetails()
        if (vType == vDuration or vType == vAllValues):
            start = parse(valStart)
            stop = parse(valStop)
            duration = (stop - start)
            logging.info('duration: '+str(duration))
            trackDetails.duration = duration

        if (vType == vDistance or vType == vAllValues):
            logging.info('distance: '+str(distance))
            trackDetails.distance = distance

        if (vType == vMaxElevation or vType == vAllValues):
            em = float(-9999.0)
            for e in elevations:
                fe = float(e)
                if fe > em:
                    em = fe
            trackDetails.elevation_max = em

        if (vType == vMinElevation or vType == vAllValues):
            em = float(9999.0)
            for e in elevations:
                fe = float(e)
                if fe < em:
                    em = fe
            trackDetails.elevation_min = em

        return trackDetails

    def getAllTrackDetails(self, blob_key):
        return self.getVal(blob_key, vAllValues)

    def getMaxElevation(self, blob_key):
        return self.getVal(blob_key, vMaxElevation)

    def getMinElevation(self, blob_key):
        return self.getVal(blob_key, vMinElevation)

    def getDuration(self, blob_key):
        return self.getVal(blob_key, vDuration)

    def getDistance(self, blob_key):
        """ Uses Equirectangular approximation. Precise enough only for small
        distances see http://www.movable-type.co.uk/scripts/latlong.html """
        return self.getVal(blob_key, vDistance)

    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        blob_key = blob_info.key()

        td = self.getAllTrackDetails(blob_key)

        templateVals = {
            'doctype' : doctype,
            'meta_tag' : meta_tag,

            'file_name' : blob_info.filename,
            'timestamp' : 'timestamp',
            'location' : 'location',
            'avrg_speed' : 'avrg_speed',
            'duration' : td.duration,
            'distance' : td.distance,
            'top_speed' : 'top_speed',
            'total_ascending' : 'total_ascending',
            'total_descending' : 'total_descending',
            'elevation_gain' : (td.elevation_max - td.elevation_min),

            'distanceUnits' : distanceUnits,
            'elevationUnits' : elevationUnits,
            'speedUnits' : speedUnits,
        }
        template = jinja_environment.get_template('/templates/details.html')
        self.response.out.write(template.render(templateVals))


class Delete(webapp2.RequestHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        blob_key = blob_info.key()
        blobstore.delete(blob_key)
        self.redirect('/')


class Download(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info, save_as=blob_info.filename)

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

        logging.info('XSD file read in.')

        psviResult = ''
        elementTree = ''
        root = ''
        try:
            # use default values of minixsv, location of the schema file must
            # be specified in the XML file
            #domTreeWrapper = pyxsval .parseAndValidate ("Test.xml")

            # domTree is a minidom document object
            #domTree = domTreeWrapper.getTree()

            # call validator with non-default values
            psviResult = elementTreeWrapper = pyxsval.parseAndValidateString(
            #psviResult = pyxsval.parseAndValidateString(
                inputText, xsdText,
                #xmlIfClass= pyxsval.XMLIF_ELEMENTTREE,
                #warningProc=pyxsval.PRINT_WARNINGS,
                #errorLimit=200, verbose=1,
                #useCaching=0, processXInclude=0
                )

            #logging.info('done: ')
            elementTreeWrapper = psviResult
            # get elementtree object after validation
            elementTree = elementTreeWrapper.getTree()
            root = elementTreeWrapper.getRootNode()

        except pyxsval.XsvalError, errstr:
            print errstr
            logging.error("Validation aborted!")

        except GenXmlIfError, errstr:
            print errstr
            logging.error("Parsing aborted!")

        except db.Timeout, errstr:
            #except (db.Timeout, db.InternalError):
            #except datastore_errors.Timeout, errstr:
            print errstr
            logging.error('Timeout-specific error page')

        # redirect back to the upload page
        #self.redirect('/')

        #logging.info('elementTree: '+str(elementTree))
        #logging.info('---------------------- root: '+str(root))
        #eleList = root.getXPath('trk')

        #eleList = root.getElementsByTagName()
        #logging.info('---- : '+ str(eleList))
        #for ele in eleList:
            #s = str(ele)
            #logging.info('---- : '+ s)

        elevations = []
        rootChildren = root.getChildren()
        for root_c in rootChildren:
            s = root_c.getTagName()
            #logging.info('---- : '+ s)
            if s == "trk":
                trkChildren = root_c.getChildren()
                for trk_c in trkChildren:
                    s = trk_c.getTagName()
                    #logging.info('---- ---- : '+ s)
                    if s == "trkseg":
                        trkseqChildren = trk_c.getChildren()
                        for trkseq_c in trkseqChildren:
                            #s = trkseq_c.getTagName()
                            #logging.info('---- ---- ---- : '+ s)
                            #lon = trkseq_c.getAttribute("lon")
                            #lat = trkseq_c.getAttribute("lat")
                            #logging.info('---- ---- ---- : '+ 'lon :'+lon + ' lat: '+lat)
                            trkptChildren = trkseq_c.getChildren()
                            for trkpt_c in trkptChildren:
                                s = trkpt_c.getTagName()
                                #logging.info('---- ---- ---- ---- : '+ s)
                                if s == "ele":
                                    ele_v = trkpt_c.getElementValue()
                                    #logging.info('---- ---- ---- ---- : '+ str(ele_v))
                                    elevations.append(ele_v)


        em = float(-9999.0)
        e_min = float(9999.0)
        for e in elevations:
            fe = float(e)
            if fe < e_min:
                e_min = fe
            if fe > em:
                em = fe

        logging.info('elevation.size: '+str(len(elevations)))
        logging.info('em: '+ str(em)+'; e_min: '+ str(e_min))

        # display the gpxtrack on the maplayer
        self.redirect('/maplayer/'+str(blob_key))

    #def handle_exception(self, exception, debug_mode):
        #if debug_mode:
            #super(ServeHandler, self).handle_exception(exception, debug_mode)
        #else:
            #if isinstance(exception, datastore_errors.Timeout):
                ## Display a timeout-specific error page
                #logging.error('timeout-specific error page')
            #else:
                ## Display a generic 500 error page.
                #logging.error('generic 500 error page')


def main():
    application = webapp2.WSGIApplication([
        ('/', MainHandler),
        ('/test', Test),
        ('/details/([^/]+)?', Details),
        ('/delete/([^/]+)?', Delete),
        ('/download/([^/]+)?', Download),
        ('/upload_handler', UploadHandler),
        ('/servefile/([^/]+)?', ServeHandler),
        ], debug=True)
    #run_wsgi_app(application)
    return application

if __name__ == '__main__':
    main()

app = main()
