from __future__ import with_statement
from google.appengine.api import files

import logging
import cgi
import webapp2
import urllib

from google.appengine.ext import blobstore
from google.appengine.ext import db
from google.appengine.api import mail

import jinja2
import os
from upload import Details

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


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


def inc_cnt():
    global globCnt    # this is needed to modify global copy of globvar
    globCnt = globCnt + 1


def reset_cnt():
    global globCnt
    globCnt = 0

class GeoLocation(db.Model):
    lon = db.StringProperty()
    lat = db.StringProperty()
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
            s = s + "<p>"+loc.lat + ", " + loc.lon +"</p>"
        count = GeoLocation.all(keys_only=True).count()
        s = "<html><body>"+str(count)+" stored positions:</br>"+s+"</body></head></html>"
        self.response.out.write(s)


class Store(webapp2.RequestHandler):
    def get(self):
        cnt = 0
        s = ""
        for position in positions:
            geo_location = GeoLocation()
            geo_location.lon = str(position[0])
            geo_location.lat = str(position[1])
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


class MapLayer(webapp2.RequestHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        blob_key = blob_info.key()

        gpxTrackUrl = '/gpxtrack/'+ str(blob_key)
        logging.info('gpxTrackUrl: '+gpxTrackUrl)

        cntGpsPositions = "1"
        #cntGpsPositions = str(len(positions) - 1)

        logging.info("length: "+cntGpsPositions)
        reset_cnt()

        details = Details()
        td = details.getStartLocation(blob_key)
        templateVals = {
            'cntGpsPositions' : cntGpsPositions,
            'style' : "width:100%; height:100%",
            'lon' : td.startLon,
            'lat' : td.startLat,
            'zoom' : 16,
            'gpxTrackUrl' : gpxTrackUrl,
        }

        template = jinja_environment.get_template('/templates/maplayer.html')
        #template = jinja_environment.get_template('/templates/layout.html')
        self.response.out.write(template.render(templateVals))


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
                tags += "<trkpt lat=\""+loc.lat+"\" lon=\""+loc.lon+"\">"
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

# This class is called indirectly from javascript
class GpxTrack(webapp2.RequestHandler):
    def get(self, resource):
        logging.info('GpxTrack {')
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        blob_key = blob_info.key()
        blob_reader = blobstore.BlobReader(blob_key)
        respData = blob_reader.read()
        self.response.out.write(respData)
        logging.info('GpxTrack }')


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



class Templates(webapp2.RequestHandler):
    def get(self):
        guestbook_name=self.request.get('guestbook_name')
        greetings_query = Greeting.all().ancestor(
            guestbook_key(guestbook_name)).order('-date')
        greetings = greetings_query.fetch(10)

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        templateVals = {
            'greetings': greetings,
            'url': url,
            'url_linktext': url_linktext,
        }

        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(templateVals))


def main():
    application = webapp2.WSGIApplication([
        ('/maplayer/([^/]+)?', MapLayer),
        ('/gpxtrack/([^/]+)?', GpxTrack),
        ('/store', Store),
        ('/show', Show),
        ('/clear', Clear),
        ('/email', Email),
        ('/templates', Templates),
        ], debug=True)
    #run_wsgi_app(application)
    return application

if __name__ == '__main__':
    main()

app = main()

