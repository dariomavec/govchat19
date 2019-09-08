fetch('https://3jaz6s2dul.execute-api.ap-southeast-2.amazonaws.com/dev/trams')
.then(res => res.json())
.then(data => {
	})


fetch('https://raw.githubusercontent.com/uber-common/deck.gl-data/master/examples/arc/counties.json')
.then(res => res.json())
.then(data => {
	console.log(data);

  const inFlowColors = [
    [255, 255, 204],
    [199, 233, 180],
    [127, 205, 187],
    [65, 182, 196],
    [29, 145, 192],
    [34, 94, 168],
    [12, 44, 132]
  ];

  const outFlowColors = [
    [255, 255, 178],
    [254, 217, 118],
    [254, 178, 76],
    [253, 141, 60],
    [252, 78, 42],
    [227, 26, 28],
    [177, 0, 38]
  ];

  const countyLayer = new deck.GeoJsonLayer({
    id: 'geojson',
    data,
    stroked: false,
    filled: true,
    autoHighlight: true,
    getFillColor: () => [0, 0, 0, 0],
    onClick: info => updateLayers(info.object),
    pickable: true
  });

  const tripsLayer = new deck.TripsLayer({
    id: 'trips-layer',
    data,
    getPath: d => d.waypoints.map(p => p.coordinates),
    // deduct start timestamp from each data point to avoid overflow
    getTimestamps: d => d.waypoints.map(p => p.timestamp - 1554772579000),
    getColor: [253, 128, 93],
    opacity: 0.8,
    widthMinPixels: 5,
    rounded: true,
    trailLength: 200,
    currentTime: 100
  });

  const deckgl = new deck.DeckGL({
		container: 'deckgl-graph-01',
    mapboxApiAccessToken: 'pk.eyJ1IjoidWJlcmRhdGEiLCJhIjoiY2pudzRtaWloMDAzcTN2bzN1aXdxZHB5bSJ9.2bkj3IiRC8wj3jLThvDGdA',
    mapStyle: 'mapbox://styles/mapbox/light-v9',
    latitude: -25.27,
    longitude: 133.77,
    zoom: 2,
    maxZoom: 15,
    pitch: 30,
    bearing: 30,
    layers: []
  });

	window.deckgl = deckgl

  // updateLayers(
  //   data.features.find(f => f.properties.name === 'Los Angeles, CA')
  // );

  function updateLayers(selectedFeature) {
    const {flows, centroid} = selectedFeature.properties;

    const arcs = Object.keys(flows).map(toId => {
      const f = data.features[toId];
      return {
        source: centroid,
        target: f.properties.centroid,
        value: flows[toId]
      };
    });

    const scale = d3.scaleQuantile()
      .domain(arcs.map(a => Math.abs(a.value)))
      .range(inFlowColors.map((c, i) => i));

    arcs.forEach(a => {
      a.gain = Math.sign(a.value);
      a.quantile = scale(Math.abs(a.value));
    });

    const arcLayer = new deck.ArcLayer({
      id: 'arc',
      data: arcs,
      getSourcePosition: d => d.source,
      getTargetPosition: d => d.target,
      getSourceColor: d => (d.gain > 0 ? inFlowColors : outFlowColors)[d.quantile],
      getTargetColor: d => (d.gain > 0 ? outFlowColors : inFlowColors)[d.quantile],
      strokeWidth: 4
    });

    deckgl.setProps({
      layers: [countyLayer, tripsLayer]
    });
  }
});
