#!/usr/bin/env python
from __future__ import with_statement

import logging
import os
import urllib
import webapp2
import jinja2

from google.appengine.api import users
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


detailId_prefix = 'detail'
cboxId_prefix = 'cbox'

# Earth radius in kilometer
R = 6371
undef = -1

global isDevelopment
isDevelopment = False

colors = [
    'red', 'blue', 'black', 'fuchsia', 'gray', 'lime', 'maroon',
    'navy', 'olive', 'purple', 'silver', 'teal', ];

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


def getFileContent(path):
    os_path = os.path.join(os.path.split(__file__)[0], path)
    s = file(os_path, 'r').read()
    #logging.info('-----------------s: '+s)
    return s

class TrackValues(db.Model):
    filename = db.StringProperty()
    timestamp = db.DateTimeProperty(auto_now_add=True)
    location = undef
    waypoints = db.IntegerProperty()
    startLon = db.FloatProperty()
    startLat = db.FloatProperty()
    speed_avrg = db.FloatProperty()
    #duration = db.TimeProperty()   # TODO duration needs to be a TimeProperty
    duration = db.StringProperty()
    distance = db.FloatProperty()
    speed_max = db.FloatProperty()
    total_ascending = undef
    total_descending = undef
    #elevation_gain = db.FloatProperty()
    elevation_max = db.FloatProperty()
    elevation_min = db.FloatProperty()
    blob_key = db.StringProperty()
    time = db.StringProperty()

# TODO track display
class TrackDisplay(db.Model):
    blob_key = db.StringProperty()
    show = db.BooleanProperty()

class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            #self.response.out.write('Hello, ' + user.nickname())
            #self.response.headers['Content-Type'] = 'text/plain'
            logging.info('Current user: '+user.nickname())
            display = Display()
            blob_key = undef
            s = display.doDisplay(self.request, blob_key)
            self.response.out.write(s)
        else:
            logging.info('The user is not logged in. Redirecting...')
            url = users.create_login_url(self.request.uri)
            #url_linktext = 'Login'
            #greeting = ("<a href=\"%s\">Sign in or register</a>." % users.create_login_url("/"))
            #self.response.out.write("<html><body>%s</body></html>" % greeting)
            self.redirect(url)


# TODO Display should consist of displayMap and displayDetails
class Display(webapp2.RequestHandler):
    def get(self, blob_key):
        self.doDisplay(self.request, blob_key)

    def doDisplay(self, request, blob_key):
        user = users.get_current_user()
        if not user:
            logging.error('---------> The user is not logged in. This should not happen :-(')
            url = users.create_login_url(request.uri)
            url_linktext = 'Login'
            self.redirect(url)

        logging.info('Display <')
        uploadHandlerUrl = blobstore.create_upload_url('/upload_handler')
        all_blobs = blobstore.BlobInfo.all()

        values = TrackValuesCalculator()
        mapEntries = []
        for idx, b in enumerate(all_blobs):
            bKey = b.key()
            td = values.getAllTrackValues(bKey)
            # 2012-08-23T15:27:01.000Z
            cn  = td.time[8:10] + '.'
            cn += td.time[5:7] + '.'
            cn += td.time[0:4] + ' '
            cn += td.time[11:16]

            mapEntry = {
                'lon' : td.startLon,
                'lat' : td.startLat,
                'bKey' : str(bKey),
                'bFilename' : cn,
                'time' : td.time,
                'idx' : idx,
                'cboxId' : 'cbox'+str(idx),
                'detailId' : detailId_prefix+str(idx),
                'color' : colors[idx],

                'detailId' : detailId_prefix+str(idx),
                'filename' : td.filename,
                'timestamp' : 'timestamp',
                'waypoints' : td.waypoints,
                'location' : 'location',
                'speed_avrg' : td.speed_avrg,
                'duration' : td.duration,
                'distance' : td.distance,
                'speed_max' : td.speed_max,
                'total_ascending' : 'total_ascending',
                'total_descending' : 'total_descending',
                'elevation_gain' : (td.elevation_max - td.elevation_min),
            }
            mapEntries.append(mapEntry)

        sortedMapEntries = mapEntries
        #sortedMapEntries = sorted(mapEntries, key=lambda a_entry: a_entry['time'])

        #logging.info('mapEntries: '+ str(sortedMapEntries))
        url = users.create_logout_url(request.uri)
        url_linktext = 'Logout'
        nickname = user.nickname()
        #self.response.headers['Content-Type'] = 'text/plain'
        templateVals = {
            'url' : url,
            'url_linktext' : url_linktext,
            'user_nickname' : nickname,
            'url_upload_handler' : uploadHandlerUrl,
            'all_blobs' : all_blobs,
            'entries' : sortedMapEntries,
            'url_maplayer' : 'maplayer',
            'url_delete' : 'delete',
            'url_download' : 'download',
            'url_details' : 'values',
            'distanceUnits' : distanceUnits,
            'elevationUnits' : elevationUnits,
            'speedUnits' : speedUnits,
        }
        template = jinja_environment.get_template('templates/layout.html')
        s = template.render(templateVals)
        logging.info('Display >')
        if blob_key == undef:
            return s
        else:
            self.response.out.write(s)



class TrackValuesCalculator(webapp2.RequestHandler):
    def calcSpeed(self, distance, time):
        return float(distance) / float(time)

    def deg2rad(self, degree):
        """ GPS coordinates in the gpx files are in degrees, calculation are
        made in radians """
        return (pi * float(degree) / 180.0)

    def getVal(self, blob_key, vType=1):
        logging.info('TrackValuesCalculator.getVal <')

        results = db.GqlQuery('SELECT * FROM TrackValues WHERE blob_key = :1', blob_key)
        for tdResult in results:
            logging.info('TrackValues already calculated. blob_key '+str(blob_key)+'; filename: '+tdResult.filename)
            logging.info('TrackValuesCalculator.getVal >')
            return tdResult

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

        values = TrackValues()
        values.waypoints = 0
        rootChildren = root.getChildren()
        for root_c in rootChildren:
            tagName = root_c.getTagName()
            if tagName == "metadata":
                metadataChildren = root_c.getChildren()
                for metadata_c in metadataChildren:
                    tagName = metadata_c.getTagName()
                    if tagName == "name":
                        values.filename = metadata_c.getElementValue()
                    elif tagName == "time":
                        values.time = metadata_c.getElementValue()

            elif tagName == "trk":
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

                                values.waypoints += 1

                                if lat1 == undef:
                                    values.startLon = lon_degree
                                    values.startLat = lat_degree

                                    if vType == vStartLocation:
                                        return values

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
                                            timeDiff = (time2 - time1)
                                            minutes = (float(timeDiff.seconds) / 60)
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
            values.duration = str(duration)

        if vType == vDistance or vType == vAllValues:
            logging.info('distance: '+str(distanceTotal))
            values.distance = distanceTotal

        if vType == vMaxElevation or vType == vAllValues:
            values.elevation_max = maxElev

        if vType == vMinElevation or vType == vAllValues:
            values.elevation_min = minElev

        if vType == vSpeedMax or vType == vAllValues:
            values.speed_max = speedMax

        if vType == vSpeedAvrg or vType == vAllValues:
            values.speed_avrg = float(speedSum / cntMeasurements)
            logging.info('speed_avrg: '+str(values.speed_avrg))

        values.blob_key = str(blob_key)
        key = values.put();
        msg  = 'Track values put to datastore'
        msg += '; blob_key: '+str(values.blob_key)+'; filename: '+values.filename
        logging.info(msg)

        logging.info('TrackValuesCalculator.getVal >')
        return values



    def getAllTrackValues(self, blob_key):
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
        logging.info('TrackValuesCalculator.get <')
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        blob_key = blob_info.key()

        all_blobs = blobstore.BlobInfo.all()

        #values = self.getAllTrackValues(blob_key)

        values = TrackValuesCalculator()
        for idx, b in enumerate(all_blobs):
            bKey = b.key()
            if blob_key == b.key():
                td = values.getAllTrackValues(bKey)
                templateVals = {
                    'doctype' : doctype,
                    'meta_tag' : meta_tag,
                    'distanceUnits' : distanceUnits,
                    'elevationUnits' : elevationUnits,
                    'speedUnits' : speedUnits,

                    'color' : colors[idx],
                    'detailId' : detailId_prefix+str(idx),
                    'filename' : td.filename,
                    'timestamp' : 'timestamp',
                    'waypoints' : td.waypoints,
                    'location' : 'location',
                    'speed_avrg' : td.speed_avrg,
                    'duration' : td.duration,
                    'distance' : td.distance,
                    'speed_max' : td.speed_max,
                    'total_ascending' : 'total_ascending',
                    'total_descending' : 'total_descending',
                    'elevation_gain' : (td.elevation_max - td.elevation_min),
                }
                break

        template = jinja_environment.get_template('/templates/details.html')
        #template = jinja_environment.get_template('/templates/layout.html')
        self.response.out.write(template.render(templateVals))
        logging.info('TrackValuesCalculator.get >')


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
        logging.info('ServeHandler.get <')
        global isDevelopment
        blob_info = blobstore.BlobInfo.get(resource)
        blob_key = blob_info.key()

        if isDevelopment:
            # TODO run xml validation in background from task queue
            logging.debug('isDevelopment: '+str(isDevelopment)+' => no xml validation')
        else:
            resource = str(urllib.unquote(resource))
            if not blobstore.get(resource):
                self.error(404)
                return

            #for b in blobstore.BlobInfo.all():
                #blob_key = b.key()
            blob_reader = blobstore.BlobReader(blob_key)
            inputText = blob_reader.read()

            # TODO The gpx.xsd cannot be placed in a subdirectory - why?
            xsdText = getFileContent('gpx.xsd')
            logging.info('XSD file read in')

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
                logging.info('parseAndValidateString done')

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

        # display the gpxtrack using the layout template
        self.redirect('/track/'+str(blob_key))
        logging.info('ServeHandler.get >')

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
    logging.info('main <')
    global isDevelopment
    isDevelopment = os.environ['SERVER_SOFTWARE'].startswith('Development')
    logging.info('isDevelopment: '+str(isDevelopment))
    #for name in os.environ.keys():
        #self.response.out.write("%s = %s<br />\n" % (name, os.environ[name]))
    application = webapp2.WSGIApplication([
        ('/', MainHandler),
        ('/track/([^/]+)?', Display),
        ('/details/([^/]+)?', TrackValuesCalculator),
        ('/delete/([^/]+)?', Delete),
        ('/download/([^/]+)?', Download),
        ('/upload_handler', UploadHandler),
        ('/servefile/([^/]+)?', ServeHandler),
        ], debug=True)
    #run_wsgi_app(application)
    logging.info('main >')
    return application

if __name__ == '__main__':
    main()

app = main()
