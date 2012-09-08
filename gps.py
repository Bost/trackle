from __future__ import with_statement
from google.appengine.api import files

import logging
import cgi
import webapp2

from google.appengine.ext import db
from google.appengine.api import mail


global positions
positions = [    #lon, lat, time
    [9.182163060603656, 48.78253065159807, "2007-10-14T10:09:57Z"],
    [9.181182488498106, 48.78164800994976, "2007-10-14T10:09:57Z"],
    [9.179332819535709, 48.78224535223885, "2007-10-14T10:09:57Z"],
    [9.178585251645632, 48.78146605455337, "2007-10-14T10:09:57Z"],
    [9.177577231901306, 48.78029765057715, "2007-10-14T10:09:57Z"],
    [9.175750335509962, 48.77983208606208, "2007-10-14T10:09:57Z"],
    [9.175100098496504, 48.78067884694779, "2007-10-14T10:09:57Z"],
    [9.173643038322766, 48.78022415496748, "2007-10-14T10:09:57Z"],
    [9.174046288736349, 48.77949238611516, "2007-10-14T10:09:57Z"],
    [9.174969289402229, 48.77850433775755, "2007-10-14T10:09:57Z"],
]

global globCnt
globCnt = 0

trackUrl = '/trackFromFile'
#trackUrl = '/trackFromDBase'

def inc_cnt():
    global globCnt    # this is needed to modify global copy of globvar
    globCnt = globCnt + 1


def reset_cnt():
    global globCnt
    globCnt = 0

class GeoLocation(db.Model):
    longitude = db.StringProperty()
    latitude = db.StringProperty()
    timestamp = db.StringProperty()
    device_key = db.StringProperty()
    device_label = db.StringProperty()
    altitude = db.StringProperty()
    speed = db.StringProperty()
    heading = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)

class Clear(webapp2.RequestHandler):
    def get(self):
        cntb = GeoLocation.all(keys_only=True).count()

        query = GeoLocation.all()
        entries =query.fetch(1000)
        db.delete(entries)

        cnta = GeoLocation.all(keys_only=True).count()
        s = "<html><body>"+str(cntb)+" entities deleted. New size: "+str(cnta)+"</body></head></html>"
        self.response.out.write(s)


class Show(webapp2.RequestHandler):
    def get(self):
        s = ""
        locations = db.GqlQuery('SELECT * FROM GeoLocation ORDER BY date DESC')
        for loc in locations:
            s = s + "<p>"+loc.latitude + ", " + loc.longitude +"</p>"
        count = GeoLocation.all(keys_only=True).count()
        s = "<html><body>"+str(count)+" stored positions:</br>"+s+"</body></head></html>"
        self.response.out.write(s)


class Store(webapp2.RequestHandler):
    def get(self):
        cnt = 0
        s = ""
        for position in positions:
            geo_location = GeoLocation()
            geo_location.longitude = str(position[0])
            geo_location.latitude = str(position[1])
            geo_location.timestamp = str(position[2])
            geo_location.device_key = str("")
            geo_location.device_label = "test"
            geo_location.altitude = str("")
            geo_location.speed = str("")
            geo_location.heading = str("")
            key = geo_location.put()
            if key != None:
                cnt += 1
                s += "<p>"+str(cnt)+"; key: "+str(key)+"</p>"

        count = GeoLocation.all(keys_only=True).count()
        s = "<html><body>"+str(count)+" rows stored."+s+"</body></head></html>"
        self.response.out.write(s)


class MainPage(webapp2.RequestHandler):
    def get(self):
        #resource = str(urllib.unquote(resource))
        #blob_info = blobstore.BlobInfo.get(resource)

        #trackUrl = "/data/runtastic_20120823_1715_MountainBiking.gpx"
        #trackUrl = "/data/runtastic_20120829_1725_MountainBiking.gpx"
        cntGpsPositions = "1"
        #cntGpsPositions = str(len(positions) - 1)

        logging.info("length: "+cntGpsPositions)
        reset_cnt()

        style = "width:100%; height:100%"
        s = """
<html>
<head>
	<title>Simple OSM GPX Track</title>
	<!-- bring in the OpenLayers javascript library
		 (here we bring it from the remote site, but you could
		 easily serve up this javascript yourself) -->
	<script src="http://www.openlayers.org/api/OpenLayers.js"></script>
	<!-- bring in the OpenStreetMap OpenLayers layers.
		 Using this hosted file will make sure we are kept up
		 to date with any necessary changes -->
	<script src="http://www.openstreetmap.org/openlayers/OpenStreetMap.js"></script>
	<script type="text/javascript" src="js/script.js"></script>
</head>
	<!-- body.onload is called once the page is loaded (call the 'init' function) -->
	<body onload="init(%s, '%s');">
	<!-- define a DIV into which the map will appear. Make it take up the whole window -->
	<div style="%s" id="map"></div>
</body>
</html>
""" % (cntGpsPositions, trackUrl, style)
        self.response.out.write(s)


class TrackFromDBase(webapp2.RequestHandler):
    def get(self):
        global globCnt
        #logging.info("{} {}".format(positions[globCnt][1], positions[globCnt][0]) )
        #this select selects too many rows - i just use two of them
        locations = db.GqlQuery('SELECT * FROM GeoLocation ORDER BY date ASC')

        cnt = 0
        tags = ""
        for loc in locations:
            if cnt == globCnt or cnt == globCnt + 1:
                tags += "<trkpt lat=\""+loc.latitude+"\" lon=\""+loc.longitude+"\">"
                tags += "<ele></ele><time>"+str(loc.date)+"</time></trkpt>"
            if cnt == globCnt:
                tags += "\n\t\t\t"
            cnt += 1

        s = """
<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.0">
    <name>Example gpx</name>
    <wpt lat="48.78224865627344" lon="9.181918049511319">
        <ele>2372</ele>
        <name>LAGORETICO</name>
    </wpt>
    <trk>
        <name>Example gpx</name><number>1</number>
        <trkseg>
            %s
        </trkseg>
    </trk>
</gpx>
""" % (tags)
        #logging.info("s: "+s)
        self.response.out.write(s)

class TrackFromFile(webapp2.RequestHandler):
    def get(self):
        filename = '/gs/data/tmpfile'
        params = {'date-created':'092011', 'owner':'Jon'}
        logging.info('Opening file: '+filename)

        respData = ""
        with files.open(filename, 'r') as f:
            data = f.read(1000)
            respData += data
            while data != "":
                #print data
                data = f.read(1000)
                respData += data

        #logging.info("respData: "+respData)
        self.response.out.write(respData)


class Email(webapp2.RequestHandler):
    def get(self):
        message = mail.EmailMessage(sender="",
                                    subject="App Engine sending email")
        message.to = ""
        message.body = """
        Here come is the email body
        """
        message.send()
        s = "<html><body>Email sent</body></head></html>"
        self.response.out.write(s)


class Upload(webapp2.RequestHandler):
    def get(self):
        s = """
<html><body>
<div><input type="file" name="userfile"/></div>
<div><input type="submit" value="send"/></div>
</body></head></html>
"""
        self.response.out.write(s)

class UploadResponse(webapp2.RequestHandler):
    def post(self):
        c = self.request.get("content")
        u = self.request.get("userfile")
        s = "<html><body>"+s+"</body></head></html>"
        self.response.out.write(s)

app = webapp2.WSGIApplication(
        [
            ('/gps', MainPage),
            (trackUrl, TrackFromFile),
            #(trackUrl, TrackFromDBase),
            ('/store', Store),
            ('/show', Show),
            ('/clear', Clear),
            ('/email', Email)
            ,('/upload', Upload),
            ],
        debug=True)

