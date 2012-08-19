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
			//url: "./data/around_lake.py",
			url: "./data/around_lake.gpx",
			format: new OpenLayers.Format.GPX()
		}),
		style: {strokeColor: "green", strokeWidth: 5, strokeOpacity: 0.5},
		projection: new OpenLayers.Projection("EPSG:4326")
	});
	//map.addLayer(lgpx);

	var featurecollection = 
	{
		"type": "FeatureCollection",
		"features": [
			{
				//"type": "Feature",
				//"properties": { 
					//"name": "Example gpx", "cmt": "", "desc": "", "src": "", "link1_href": "", "link1_text": "", "link1_type": "", "link2_href": "", "link2_text": "", "link2_type": "", "number": 1, "type": "" 
				//},
				"geometry": {

					"type": "MultiLineString",
					"coordinates": [
						[ [ 9.181918, 48.782249 ], [ 9.181268, 48.781602 ], [ 9.179366, 48.782316 ], [ 9.178597, 48.781473 ], [ 9.177436, 48.780203 ] ]
					]
				}
			}
		]
	}
	;
		
	var fc = {
	  "type": "FeatureCollection",
	  "features": [
		{
			"geometry": {
				"type": "GeometryCollection",
				"geometries": [
					{	"type": "LineString",
						"coordinates":	[[11.0878902207, 45.1602390564],
										[15.01953125, 48.1298828125]]
					},
					{	"type": "Polygon",
						"coordinates":	[[[11.0878902207, 45.1602390564],
										  [14.931640625, 40.9228515625],
										  [0.8251953125, 41.0986328125],
										  [7.63671875, 48.96484375],
										  [11.0878902207, 45.1602390564]]]
					},
					{	"type":"Point",
						"coordinates":[9.17743640333, 48.7802032105]
					}
				]
			},
			"type": "Feature",
			"properties": {}
		}
	  ]
	};

	var geojson_format = new OpenLayers.Format.GeoJSON();
	var vector_layer = new OpenLayers.Layer.Vector();
	map.addLayer(vector_layer);
	vector_layer.addFeatures(geojson_format.read(featurecollection));

	var lonLat = new OpenLayers.LonLat(lon, lat).transform(new OpenLayers.Projection("EPSG:4326"), map.getProjectionObject());
	map.setCenter(lonLat, zoom);

	var size = new OpenLayers.Size(21, 25);
	var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
	var icon = new OpenLayers.Icon('http://www.openstreetmap.org/openlayers/img/marker.png',size,offset);
	layerMarkers.addMarker(new OpenLayers.Marker(lonLat,icon));
}
