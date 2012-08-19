import logging
import cgi
import webapp2
from time import sleep

from google.appengine.api import users


global the_list
the_list = [
    [9.182163060603656,48.78253065159807],
    [9.181182488498106,48.78164800994976],
    [9.179332819535709,48.78224535223885],
    [9.178585251645632,48.78146605455337],
    [9.177577231901306,48.78029765057715],
    [9.175750335509962,48.77983208606208],
    [9.175100098496504,48.78067884694779],
    [9.173643038322766,48.78022415496748],
    [9.174046288736349,48.77949238611516],
    [9.174969289402229,48.77850433775755],
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

	<script type="text/javascript">
	// Start position for the map (hardcoded here for simplicity,
	// but maybe you want to get this from the URL params)
	var lat=48.78224865627344
	var lon=9.181918049511319
	var zoom=16

	var map; //complex object of type OpenLayers.Map

	function myFn() {
		// Add the Layer with the GPX Track
		var lgpx = new OpenLayers.Layer.Vector("Lakeside cycle ride", {
			strategies: [new OpenLayers.Strategy.Fixed()],
			protocol: new OpenLayers.Protocol.HTTP({
				url: "track",
				format: new OpenLayers.Format.GPX()
			}),
			style: {strokeColor: "green", strokeWidth: 5, strokeOpacity: 0.7},
			projection: new OpenLayers.Projection("EPSG:4326")
		});
		map.addLayer(lgpx);
	}

	function init() {
		map = new OpenLayers.Map ("map", {
			controls:[
				new OpenLayers.Control.Navigation(),
				new OpenLayers.Control.PanZoomBar(),
				new OpenLayers.Control.LayerSwitcher(),
				new OpenLayers.Control.Attribution()],
			maxExtent: new OpenLayers.Bounds(-20037508.34,-20037508.34,20037508.34,20037508.34),
			maxResolution: 156543.0399,
			numZoomLevels: 19,
			units: 'm',
			projection: new OpenLayers.Projection("EPSG:900913"),
			displayProjection: new OpenLayers.Projection("EPSG:4326")
		} );

		// Define the map layer
		// Here we use a predefined layer that will be kept up to date with URL changes
		layerMapnik = new OpenLayers.Layer.OSM.Mapnik("Mapnik");
		map.addLayer(layerMapnik);
		layerCycleMap = new OpenLayers.Layer.OSM.CycleMap("CycleMap");
		map.addLayer(layerCycleMap);
		layerMarkers = new OpenLayers.Layer.Markers("Markers");
		map.addLayer(layerMarkers);

		var lonLat = new OpenLayers.LonLat(lon, lat).transform(new OpenLayers.Projection("EPSG:4326"), map.getProjectionObject());
		map.setCenter(lonLat, zoom);

		var size = new OpenLayers.Size(21, 25);
		var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
		var icon = new OpenLayers.Icon('http://www.openstreetmap.org/openlayers/img/marker.png',size,offset);
		layerMarkers.addMarker(new OpenLayers.Marker(lonLat,icon));

		var time_inc = 500   // in milisec
		var time = 0

		for (var i = 0; i < 
        """
        self.response.out.write(s)
        self.response.out.write("%d" % (len(the_list) - 1))
        s = """
		; i++) {
			time += time_inc
			setTimeout(
				function() {myFn(i, time)},
				time);
			console.log("Cycle nr: " + i +"; time: "+time);
		}
	}
	</script>

</head>
<!-- body.onload is called once the page is loaded (call the 'init' function) -->
<body onload="init();">
	<!-- define a DIV into which the map will appear. Make it take up the whole window -->
	<div style="width:90%; height:90%" id="map"></div>
</body>
</html>
"""
        self.response.out.write(s)



class Track(webapp2.RequestHandler):
    def get(self):
        logging.info("{} {}".format(the_list[i][1], the_list[i][0]) )
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
			<trkpt lat="%s" lon="%s"><ele>2376</ele><time>2007-10-14T10:09:57Z</time></trkpt>
			<trkpt lat="%s" lon="%s"><ele>2376</ele><time>2007-10-14T10:09:57Z</time></trkpt>
		</trkseg>
	</trk>
</gpx>
""" % (the_list[i][1], the_list[i][0], 
       the_list[i+1][1], the_list[i+1][0])
        #logging.info(s)
        self.response.out.write(s)
        inc_cnt()



app = webapp2.WSGIApplication([('/', MainPage),
                              ('/track', Track)],
                              debug=True)
