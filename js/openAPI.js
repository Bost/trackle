function loadAPI(lat, lon) {
    var openLayers_js = "http://www.openlayers.org/api/OpenLayers.js";
    $.cachedScript(openLayers_js).done(function(script, textStatus) {
        console.log('Loading OpenLayers.js: '+textStatus );
        var openStreetMap_js = "http://www.openstreetmap.org/openlayers/OpenStreetMap.js";
        $.cachedScript(openStreetMap_js).done(function(script, textStatus) {
            console.log('Loading OpenStreetMap.js: '+textStatus );
        });
    });
}

// Add the Layer with the GPX Track
function displayTrack(url, color, map) {
    var lgpx = new OpenLayers.Layer.Vector("", {
        strategies: [new OpenLayers.Strategy.Fixed()],
        protocol: new OpenLayers.Protocol.HTTP({
            url: url,
            format: new OpenLayers.Format.GPX()
        }),
        style: {strokeColor: color, strokeWidth: 5, strokeOpacity: 0.7},
        projection: new OpenLayers.Projection("EPSG:4326")
    });
    map.addLayer(lgpx);
    console.log("Track url '"+url+"'; color '"+color+"' added to elemId '"+map+"'");
}

$.cachedScript = function(url, result, options) {
    // allow user to set any option except for dataType, cache, and url
    options = $.extend(options || {}, {
        dataType: "script",
        cache: true,
        url: url,
    });

    // Use $.ajax() since it is more flexible than $.getScript
    // Return the jqXHR object so we can chain callbacks
    return $.ajax(options);
};

function displayTracks(cntGpsPositions, lon, lat, zoom, arrUrlGpxTrack, arrUrlDetail, arrColor) {

    var map; //complex object of type OpenLayers.Map

    var mapId = 'map';
    $('#'+mapId).html('');
    map = new OpenLayers.Map (mapId, {
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
            function() { myFn(arrUrlGpxTrack, colors) },
            time);
        //console.log("Cycle nr: " + i +"; time: "+time);
    }
    */

    for(var i in arrUrlGpxTrack) {
        var url = arrUrlGpxTrack[i];
        var color = arrColor[i];

        // Add the Layer with the GPX Track
        var lgpx = new OpenLayers.Layer.Vector("", {
            strategies: [new OpenLayers.Strategy.Fixed()],
            protocol: new OpenLayers.Protocol.HTTP({
                url: url,
                format: new OpenLayers.Format.GPX()
            }),
            style: {strokeColor: color, strokeWidth: 5, strokeOpacity: 0.7},
            projection: new OpenLayers.Projection("EPSG:4326")
        });
        map.addLayer(lgpx);
        console.log("Track url '"+url+"'; color '"+color+"' added to elemId '"+mapId+"'");
    }

/*
 *    var detailId = 'detailContainer';
 *    $('#'+detailId).html('');
 *    for(var i in arrUrlDetail) {
 *        var url = arrUrlDetail[i];
 *
 *        var id = 'detailValues'+i;
 *        $('#'+detailId).append('<div class="detailValues" id="'+id+'"></div>');
 *        $('#'+id).load(url, function() {
 *            console.log("Detail url '"+url+"' appened to elemId '"+detailId+"'");
 *        });
 *    }
 */

}
