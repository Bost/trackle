import cgi
import webapp2
from time import sleep

from google.appengine.api import users

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("""
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

    <link rel="stylesheet" href="http://dev.openlayers.org/releases/OpenLayers-2.11/theme/default/style.css" type="text/css">
    <link rel="stylesheet" href="http://dev.openlayers.org/releases/OpenLayers-2.11/examples/style.css" type="text/css">
    <script src="http://dev.openlayers.org/releases/OpenLayers-2.11/lib/OpenLayers.js"></script>

	<script type="text/javascript" src="./js/script.js"></script>
</head>
<!-- body.onload is called once the page is loaded (call the 'init' function) -->
<!--<body onload="init();JavaScript:timedRefresh(5000);">-->
<body onload="init()">
	<!-- define a DIV into which the map will appear. Make it take up the whole window -->
	<div style="width:90%; height:90%" id="map"></div>
</body>
</html>
		  """)


class Guestbook(webapp2.RequestHandler):
    def post(self):
        self.response.out.write('<html><body>You wrote:<pre>')
        self.response.out.write(cgi.escape(self.request.get('content')))
        self.response.out.write('</pre></body></html>')

app = webapp2.WSGIApplication([('/', MainPage),
                              ('/sign', Guestbook)],
                              debug=True)
