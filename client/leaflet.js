var map = L.map('map', { zoomControl:false }).setView([-35.4735, 149.0124], 5);

var OpenStreetMap_Mapnik = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
	minZoom: 11,
	maxZoom: 11,
	attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
});

OpenStreetMap_Mapnik.addTo(map)

fetch('https://3jaz6s2dul.execute-api.ap-southeast-2.amazonaws.com/dev/trams')
.then(res => res.json())
.then(data => {
        data.forEach((item) => {
          console.log(item.stopInfo.stop_name)

          L.marker([item.stopInfo.stop_lat, item.stopInfo.stop_lon],
           { title: item.stopInfo.stop_name })
           .addTo(map)
        })
	})

