import logging
import cgi
import webapp2
from time import sleep

from google.appengine.api import users


global the_list
the_list = [
    [9.182163060603656,48.78253065159807, "2007-10-14T10:09:57Z"],
    [9.181182488498106,48.78164800994976, "2007-10-14T10:09:57Z"],
    [9.179332819535709,48.78224535223885, "2007-10-14T10:09:57Z"],
    [9.178585251645632,48.78146605455337, "2007-10-14T10:09:57Z"],
    [9.177577231901306,48.78029765057715, "2007-10-14T10:09:57Z"],
    [9.175750335509962,48.77983208606208, "2007-10-14T10:09:57Z"],
    [9.175100098496504,48.78067884694779, "2007-10-14T10:09:57Z"],
    [9.173643038322766,48.78022415496748, "2007-10-14T10:09:57Z"],
    [9.174046288736349,48.77949238611516, "2007-10-14T10:09:57Z"],
    [9.174969289402229,48.77850433775755, "2007-10-14T10:09:57Z"],
]

global i
i = 0

def inc_cnt():
    global i    # Needed to modify global copy of globvar
    i = i + 1


def reset_cnt():
    global i
    i = 0


class MainPage(webapp2.RequestHandler):
    def get(self):
        logging.info("length: %d" % (len(the_list) - 1))
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
        self.response.out.write("%d" % (len(the_list) - 1))
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
        #logging.info("{} {}".format(the_list[i][1], the_list[i][0]) )
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
			<trkpt lat="%s" lon="%s"><ele></ele><time>%s</time></trkpt>
			<trkpt lat="%s" lon="%s"><ele></ele><time>%s</time></trkpt>
		</trkseg>
	</trk>
</gpx>
""" % (the_list[i][1],   the_list[i][0]  , the_list[i][2],
       the_list[i+1][1], the_list[i+1][0], the_list[i+1][2],)
        #logging.info(s)
        self.response.out.write(s)
        inc_cnt()



app = webapp2.WSGIApplication([('/', MainPage),
                              ('/track', Track)],
                              debug=True)
