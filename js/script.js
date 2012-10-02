var map; //complex object of type OpenLayers.Map

// Add the Layer with the GPX Track
function myFn(arr, color) {
    for(var i in arr) {
        if (i >= colors.length) {
            console.error("Cannot display more than "+arr.length+" tracks");
            break;
        }
        var trackUrl = arr[i];
        console.log("trackIdx: "+i+"; trackUrl: "+trackUrl+"; color: "+color);

        var lgpx = new OpenLayers.Layer.Vector("", {
            strategies: [new OpenLayers.Strategy.Fixed()],
            protocol: new OpenLayers.Protocol.HTTP({
                url: trackUrl,
                format: new OpenLayers.Format.GPX()
            }),
            style: {strokeColor: color, strokeWidth: 5, strokeOpacity: 0.7},
            projection: new OpenLayers.Projection("EPSG:4326")
        });
        map.addLayer(lgpx);
    }
}

function init(cntGpsPositions, lon, lat, zoom, arrUrls, colors) {
    console.log("arrUrls: "+arrUrls)
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

    var projection = new OpenLayers.Projection("EPSG:4326");
    var projectionObj = map.getProjectionObject();
    var lonLat = new OpenLayers.LonLat(lon, lat).transform(projection, projectionObj);
    map.setCenter(lonLat, zoom);

    var size = new OpenLayers.Size(21, 25);
    var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
    var icon = new OpenLayers.Icon('http://www.openstreetmap.org/openlayers/img/marker.png',size,offset);
    layerMarkers.addMarker(new OpenLayers.Marker(lonLat,icon));

    // Wait a little in oder to downloaded the map for the 1st time.
    // This is probably not the right way to do it
    //setTimeout(function() {}, 1000);
/*
    var time_inc = 500   // in milisec
    var time = 0

    for (var i = 0; i < cntGpsPositions; i++) {
        time += time_inc
        setTimeout(
            function() { myFn(arrUrls, colors) },
            time);
        //console.log("Cycle nr: " + i +"; time: "+time);
    }
*/
    for(var i in arrUrls) {
        var trackUrl = arrUrls[i];
        var color = colors[i];
        console.log("below: trackIdx: "+i+"; trackUrl: "+trackUrl+"; color: "+color);

        var lgpx = new OpenLayers.Layer.Vector("", {
            strategies: [new OpenLayers.Strategy.Fixed()],
            protocol: new OpenLayers.Protocol.HTTP({
                url: trackUrl,
                format: new OpenLayers.Format.GPX()
            }),
            style: {strokeColor: color, strokeWidth: 5, strokeOpacity: 0.7},
            projection: new OpenLayers.Projection("EPSG:4326")
        });
        map.addLayer(lgpx);
    }
}

