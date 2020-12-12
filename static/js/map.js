var map; //Will contain map object.
var marker = false; ////Has the user plotted their location marker? 

//Function called to initialize / create the map.
//This is called when the page has loaded.
function initMap() {

      var centerOfMap = new google.maps.LatLng(23.722064, 90.405298);

    //Map options.
    var options = {
        center: centerOfMap, //Set center.
        zoom: 7 //The zoom value.
    };

    map = new google.maps.Map(document.getElementById('map'), options);
    google.maps.event.addListener(map, 'click', function (event) {

      var clickedLocation = event.latLng;

      if (marker === false) {
            //Create the marker.
            marker = new google.maps.Marker({
                position: clickedLocation,
                map: map,
                draggable: true //make it draggable
            });

            //Listen for drag events!
            google.maps.event.addListener(marker, 'dragend', function (event) {
                markerLocation();
            });
        } else {
            //Marker has already been added, so just change its location.
            marker.setPosition(clickedLocation);
        }
        markerLocation();
    });
}

function markerLocation() {
    var currentLocation = marker.getPosition();
    document.getElementById('lat').value = currentLocation.lat(); //latitude
    document.getElementById('lng').value = currentLocation.lng(); //longitude
}

//Load the map when the page has finished loading.
google.maps.event.addDomListener(window, 'load', initMap);