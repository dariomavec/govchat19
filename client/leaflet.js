var map = L.map('map', { zoomControl:false }).setView([-35.4735, 149.0124], 5);

var Stamen_Toner = L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/toner/{z}/{x}/{y}{r}.{ext}', {
	subdomains: 'abcd',
	minZoom: 12,
	maxZoom: 12,
	ext: 'png'
});

Stamen_Toner.addTo(map)

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

