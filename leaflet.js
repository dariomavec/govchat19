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

var landmarks = [{"LandmarkID": "way/37759005", "coords": [149.0920084, -35.2531368], "type": "hospital", "name": "Calvary Clinic"} , {"LandmarkID": "way/37759019", "coords": [149.0901169, -35.2512374], "type": "civic", "name": "Hennessy House"} , {"LandmarkID": "way/52333979", "coords": [149.1183914, -35.2804526], "type": "university", "name": "ANU College of Law - Building 7"}]
console.log(landmarks);

var hospitalMarker = L.AwesomeMarkers.icon({
    prefix: 'fa',
    icon: 'hospital',
    markerColor: 'blue'
  });

var uniMarker = L.AwesomeMarkers.icon({
    prefix: 'fa',
    icon: 'school',
    markerColor: 'green'
  });

landmarks.forEach((item) => {
   if (item.type == 'hospital') {
        console.log(item.type);
      L.marker([item.coords[1], item.coords[0]],
      { icon: hospitalMarker, zIndex: 100 })
         .addTo(map);
   }
   if (item.type == 'university'){
        console.log(item.type);
      L.marker([item.coords[1], item.coords[0]],
      { icon: uniMarker, zIndex: 100 })
         .addTo(map);
   }

})

fetch('https://3jaz6s2dul.execute-api.ap-southeast-2.amazonaws.com/dev/trams')
.then(res => res.json())
.then(data => {
        data.forEach((item) => {
          L.marker([item.stopInfo.stop_lat, item.stopInfo.stop_lon],
          { icon: greyMarker, title: item.stopInfo.stop_name, zIndex: 100 })
         .addTo(map)
        })
	})

