var map = L.map('map', { zoomControl:false }).setView([-35.4735, 149.0124], 5);

var OpenStreetMap_Mapnik = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
	minZoom: 3,
	maxZoom: 12,
	attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
});

var Esri_WorldGrayCanvas = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
	attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ',
	minZoom: 3,
	maxZoom: 13
});

Esri_WorldGrayCanvas.addTo(map)

var greyMarker = L.AwesomeMarkers.icon({
    prefix: 'fa',
    icon: 'flag',
    markerColor: 'gray'
  });

fetch('https://3jaz6s2dul.execute-api.ap-southeast-2.amazonaws.com/dev/trams')
.then(res => res.json())
.then(data => {
        data.forEach((item) => {
          L.marker([item.stopInfo.stop_lat, item.stopInfo.stop_lon],
          { icon: greyMarker, title: item.stopInfo.stop_name })
         .addTo(map)
        })
	})

