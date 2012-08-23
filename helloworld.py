import logging
import cgi
import webapp2

from google.appengine.ext import db


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
        s = "<html><body>"+str(cntb)+" entities deleted. New size: "+str(cnta)+"</body></head>"
        self.response.out.write(s)


class Show(webapp2.RequestHandler):
    def get(self):
        s = ""
        locations = db.GqlQuery('SELECT * FROM GeoLocation ORDER BY date DESC')
        for loc in locations:
            s = s + "<p>"+loc.latitude + ", " + loc.longitude +"</p>"
        count = GeoLocation.all(keys_only=True).count()
        s = "<html><body>"+str(count)+" stored positions:</br>"+s+"</body></head>"
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
        s = "<html><body>"+str(count)+" rows stored."+s+"</body></head>"
        self.response.out.write(s)


class MainPage(webapp2.RequestHandler):
    def get(self):
        logging.info("length: %d" % (len(positions) - 1))
        reset_cnt()
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
<body onload="init(
"""
        self.response.out.write(s)
        self.response.out.write("%d" % (len(positions) - 1))
        s = """
);">
	<!-- define a DIV into which the map will appear. Make it take up the whole window -->
	<div style="width:90%; height:90%" id="map"></div>
</body>
</html>
"""
        self.response.out.write(s)



class Track(webapp2.RequestHandler):
    def get(self):
        global globCnt
        #logging.info("{} {}".format(positions[globCnt][1], positions[globCnt][0]) )
        #this select selects too many rows - i just use two of them
        locations = db.GqlQuery('SELECT * FROM GeoLocation ORDER BY date ASC')

        cnt = 0
        tags = ""
        for loc in locations:
            if cnt == globCnt or cnt == globCnt + 1:
                tags += "<trkpt lat=\""+loc.latitude+"\" lon=\""+ loc.longitude +"\">"
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
        logging.info(s)
        self.response.out.write(s)
        inc_cnt()



app = webapp2.WSGIApplication(
        [('/', MainPage), ('/track', Track), ('/store', Store), ('/show', Show), ('/clear', Clear)],
        debug=True)
