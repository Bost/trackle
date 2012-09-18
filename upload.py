#!/usr/bin/env python
from __future__ import with_statement

import logging
import os
import urllib
import webapp2
import jinja2

from dateutil.relativedelta import *
from dateutil.parser import *
import datetime
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
vStartLocation = 'vStartLocation'
vAllValues = 'vAllValues'
vSpeedAvrg = 'vSpeedAvrg'
vSpeedMax = 'vSpeedMax'

distanceUnits = '[ km ]'
elevationUnits = '[ m ]'
speedUnits = '[ km/h ]'
timeUnits = '[ hh:mm:ss ]'

# Earth radius in kilometer
R = 6371
undef = -1

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class TrackDetails():
    file_name = undef
    timestamp = undef
    location = undef
    startLon = undef
    startLat = undef
    speed_avrg = undef
    duration = undef
    distance = undef
    speed_max = undef
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

        details = Details()
        entries = []
        for b in blobstore.BlobInfo.all():
            bKey = b.key()
            bFilename = b.filename
            td = details.getStartLocation(bKey)
            entry = { 'lon' : td.startLon, 'lat' : td.startLat, 'bKey' : bKey , 'bFilename' : bFilename }

            entries.append(entry)

        logging.info('entries: '+ str(entries))

        templateVals = {
            'doctype' : doctype,
            'meta_tag' : meta_tag,
            'url_upload_handler' : uploadHandlerUrl,
            'all_blobs' : all_blobs,
            'entries' : entries,
            'url_maplayer' : 'maplayer',
            'url_delete' : 'delete',
            'url_download' : 'download',
            'url_details' : 'details',
        }
        template = jinja_environment.get_template('/templates/layout.html')
        #template = jinja_environment.get_template('/templates/uploadsite.html')
        s = template.render(templateVals)
        self.response.out.write(s)


class Details(webapp2.RequestHandler):
    def calcSpeed(self, distance, time):
        return float(distance) / float(time)

    def deg2rad(self, degree):
        """ GPS coordinates in the gpx files are in degrees, calculation are
        made in radians """
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

        start = stop = valStop = undef
        lon1 = lat1 = lon2 = lat2 = undef
        time1 = time2 = undef
        speedMax = undef
        distanceTotal = 0
        minElev = float(9999.0)
        maxElev = float(-9999.0)

        cntMeasurements = 0
        speedSum = 0

        trackDetails = TrackDetails()

        rootChildren = root.getChildren()
        for root_c in rootChildren:
            tagName = root_c.getTagName()
            if tagName == "trk":
                trkChildren = root_c.getChildren()
                for trk_c in trkChildren:
                    tagName = trk_c.getTagName()
                    if tagName == "trkseg":
                        trkseqChildren = trk_c.getChildren()
                        for trkseq_c in trkseqChildren:

                            # speed calculation implies distance and time calculation
                            if vType == vDistance or vType == vSpeedAvrg or vType == vSpeedMax or vType == vAllValues or vType == vStartLocation:
                                lon1 = lon2
                                lon_degree = float(trkseq_c.getAttribute("lon"))
                                lon2 = self.deg2rad(lon_degree)

                                lat1 = lat2
                                lat_degree = float(trkseq_c.getAttribute("lat"))
                                lat2 = self.deg2rad(lat_degree)

                                if trackDetails.startLon == undef:
                                    trackDetails.startLon = lon_degree
                                    trackDetails.startLat = lat_degree

                                    if vType == vStartLocation:
                                        return trackDetails

                                #logging.info('lon_degree: '+str(lon_degree)+'; lat_degree: '+str(lat_degree))

                                if lon1 != undef and lon1 != undef:
                                    x = (lon2-lon1) * cos((lat1+lat2)/2)
                                    y = (lat2-lat1)
                                    distanceDelta = sqrt(x*x + y*y) * R
                                    distanceTotal += distanceDelta

                            trkptChildren = trkseq_c.getChildren()
                            for trkpt_c in trkptChildren:
                                tagName = trkpt_c.getTagName()

                                if tagName == "ele":
                                    if vType == vMaxElevation or vType == vAllValues:
                                        ele_v = float(trkpt_c.getElementValue())
                                        if ele_v > maxElev:
                                            maxElev = ele_v

                                    if vType == vMinElevation or vType == vAllValues:
                                        ele_v = float(trkpt_c.getElementValue())
                                        if ele_v < minElev:
                                            minElev = ele_v

                                elif tagName == "time":
                                    if vType == vDuration or vType == vSpeedAvrg or vType == vSpeedMax or vType == vAllValues:
                                        time1 = time2
                                        time2 = parse(trkpt_c.getElementValue())

                                        if time1 != undef and time2 != undef:
                                            td = (time2 - time1)
                                            minutes = (float(td.seconds) / 60)
                                            timeDelta = float(minutes / 60.0)
                                            if timeDelta == 0:
                                                sLon = str(lon_degree)
                                                sLat = str(lat_degree)
                                                s = 'No current speed calculated: timeDelta == 0; [lon, lat]: [ '+sLon+', '+sLat+' ]'
                                                logging.warning(s)
                                            else:
                                                speedCurrent = self.calcSpeed(distanceDelta, timeDelta)
                                                #logging.info('current speed: '+str(speedCurrent))
                                                speedSum += speedCurrent
                                                cntMeasurements += 1
                                                if speedCurrent > speedMax:
                                                    speedMax = speedCurrent

                                    if vType == vDuration or vType == vAllValues:
                                        time = trkpt_c.getElementValue()
                                        if start == undef:
                                            start = parse(time)
                                        else:
                                            # date parsing is done only the after the xml parsing
                                            valStop = time

        if vType == vDuration or vType == vAllValues:
            stop = parse(valStop)
            duration = (stop - start)
            logging.info('duration: '+str(duration))
            trackDetails.duration = duration

        if vType == vDistance or vType == vAllValues:
            logging.info('distance: '+str(distanceTotal))
            trackDetails.distance = distanceTotal

        if vType == vMaxElevation or vType == vAllValues:
            trackDetails.elevation_max = maxElev

        if vType == vMinElevation or vType == vAllValues:
            trackDetails.elevation_min = minElev

        if vType == vSpeedMax or vType == vAllValues:
            trackDetails.speed_max = speedMax

        if vType == vSpeedAvrg or vType == vAllValues:
            trackDetails.speed_avrg = float(speedSum / cntMeasurements)
            logging.info('speed_avrg: '+str(trackDetails.speed_avrg))

        return trackDetails



    def getAllTrackDetails(self, blob_key):
        return self.getVal(blob_key, vAllValues)

    def getMaxElevation(self, blob_key):
        return self.getVal(blob_key, vMaxElevation)

    def getMinElevation(self, blob_key):
        return self.getVal(blob_key, vMinElevation)

    def getDuration(self, blob_key):
        return self.getVal(blob_key, vDuration)

    def getStartLocation(self, blob_key):
        return self.getVal(blob_key, vStartLocation)

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
            'speed_avrg' : td.speed_avrg,
            'duration' : td.duration,
            'distance' : td.distance,
            'speed_max' : td.speed_max,
            'total_ascending' : 'total_ascending',
            'total_descending' : 'total_descending',
            'elevation_gain' : (td.elevation_max - td.elevation_min),

            'distanceUnits' : distanceUnits,
            'elevationUnits' : elevationUnits,
            'speedUnits' : speedUnits,
        }
        template = jinja_environment.get_template('/templates/details.html')
        #template = jinja_environment.get_template('/templates/layout.html')
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

        try:
            # use default values of minixsv, location of the schema file must
            # be specified in the XML file
            #domTreeWrapper = pyxsval .parseAndValidate ("Test.xml")

            # domTree is a minidom document object
            #domTree = domTreeWrapper.getTree()

            # call validator with non-default values
            pyxsval.parseAndValidateString(
                inputText, xsdText,
                #xmlIfClass= pyxsval.XMLIF_ELEMENTTREE,
                #warningProc=pyxsval.PRINT_WARNINGS,
                #errorLimit=200, verbose=1,
                #useCaching=0, processXInclude=0
                )

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
