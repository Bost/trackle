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

	<script type="text/javascript">

		function timedRefresh(timeoutPeriod) {
			setTimeout("location.reload(true);",timeoutPeriod);
		}

		// Start position for the map (hardcoded here for simplicity,
		// but maybe you want to get this from the URL params)
		//var lat=47.496792
		//var lon=7.571726
		var lat=48.78224865627344
		var lon=9.181918049511319
		var zoom=16

		var map; //complex object of type OpenLayers.Map

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

			// Add the Layer with the GPX Track
			var lgpx = new OpenLayers.Layer.Vector("Lakeside cycle ride", {
				//strategies: [new OpenLayers.Strategy.Fixed()],
				strategies: [
					new OpenLayers.Strategy.Fixed(),
					//new OpenLayers.Strategy.Refresh({force:true, interval: 400, active: true})
					//, new OpenLayers.Strategy.BBOX({ratio:2, resFactor: 3})
					],
				//strategies: [new OpenLayers.Strategy.Refresh({interval: 6000, force: true})],
				protocol: new OpenLayers.Protocol.HTTP({
					//url: "/data/around_lake.py",
					url: "/data/around_lake.gpx",
					format: new OpenLayers.Format.GPX()
				}),
				style: {strokeColor: "green", strokeWidth: 5, strokeOpacity: 0.5},
				projection: new OpenLayers.Projection("EPSG:4326")
			});
			map.addLayer(lgpx);

//            var featurecollection = {
//              "type": "FeatureCollection",
//              "features": [
//                {"geometry": {
//                    "type": "GeometryCollection",
//                    "geometries": [
////                        {
////                            "type": "LineString",
////                            "coordinates":
////                                [[11.0878902207, 45.1602390564],
////                                [15.01953125, 48.1298828125]]
////                        },
////                        {
////                            "type": "Polygon",
////                            "coordinates":
////                                [[[11.0878902207, 45.1602390564],
////                                  [14.931640625, 40.9228515625],
////                                  [0.8251953125, 41.0986328125],
////                                  [7.63671875, 48.96484375],
////                                  [11.0878902207, 45.1602390564]]]
////                        },
//                        {
//                            "type":"Point",
//							//"coordinates":[9.181918049511319, 48.78224865627344]
//							"coordinates":[9.17743640333, 48.7802032105]
//                            //"coordinates":[15.87646484375, 44.1748046875]
//                        }
//                    ]
//                },
//                "type": "Feature",
//                "properties": {}}
//              ]
//           };
//           var geojson_format = new OpenLayers.Format.GeoJSON();
//           var vector_layer = new OpenLayers.Layer.Vector();
//           /map.addLayer(vector_layer);
//           vector_layer.addFeatures(geojson_format.read(featurecollection));

			var lonLat = new OpenLayers.LonLat(lon, lat).transform(new OpenLayers.Projection("EPSG:4326"), map.getProjectionObject());
			map.setCenter(lonLat, zoom);

			var size = new OpenLayers.Size(21, 25);
			var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
			var icon = new OpenLayers.Icon('http://www.openstreetmap.org/openlayers/img/marker.png',size,offset);
			layerMarkers.addMarker(new OpenLayers.Marker(lonLat,icon));
		}
	</script>

</head>
<!-- body.onload is called once the page is loaded (call the 'init' function) -->
<body onload="init();JavaScript:timedRefresh(5000);">
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
