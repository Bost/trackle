function loadAPI(lat, lon) {
    var js = "http://maps.googleapis.com/maps/api/js?key=AIzaSyCMutkjLQVt5qnfN1lXA-7LwM47Lqloveo&sensor=false&callback=voidFn";
    $.cachedScript(js).done(function(script, textStatus) {
        console.log('Loading Google Maps JavaScript API v3: '+textStatus );
    });
}

function getMap(cntGpsPositions, lon, lat, zoom) {
    var mapOptions = {
        zoom: zoom,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        center: new google.maps.LatLng(lat, lon),
    };
    var map = new google.maps.Map(document.getElementById("map"), mapOptions);
    return map;
}

function displayTrack(url, color, map) {
    $.ajax({
        type: "GET",
        url: url,
        dataType: "xml",
        success: function(xml){
            var points = [];
            var bounds = new google.maps.LatLngBounds ();
            var xml = 
            $(xml).find("trkpt").each(function() {
                var lat = $(this).attr("lat");
                var lon = $(this).attr("lon");
                var p = new google.maps.LatLng(lat, lon);
                points.push(p);
                bounds.extend(p);
            });

            var poly = new google.maps.Polyline({
                path: points,
                strokeColor: color,
                strokeOpacity: .7,
                strokeWeight: 4
            });
            poly.setMap(map);
            //map.fitBounds(bounds); // fit bounds to track
        },
    });
    console.log("Track url '"+url+"'; color '"+color+"' added to '"+map+"'");
}

function displayTracks(cntGpsPositions, lon, lat, zoom, arrUrlGpxTrack, arrUrlDetail, arrColor) {
    var mapOptions = {
        zoom: zoom,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        center: new google.maps.LatLng(lat, lon),
    };
    var map = new google.maps.Map(document.getElementById("map"), mapOptions);
    for (var i in arrUrlGpxTrack) {
        var url = arrUrlGpxTrack[i];
        var color = arrColor[i];
        displayTrack(url, color, map);
    }
}

$.cachedScript = function(url, options) {
    // allow user to set any option except for dataType, cache, and url
    options = $.extend(options || {}, {
        dataType: "script",
            cache: true,
            url: url
    });

    // Use $.ajax() since it is more flexible than $.getScript
    // Return the jqXHR object so we can chain callbacks
    return $.ajax(options);
};

function voidFn() { console.log('Callback function executed: voidFn()'); }

