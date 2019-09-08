var socket;
var username = ["Jane_C","Sam_P","Timothy_D","Emmanuel_K","Phil_A","Steve_W","Shelley_S","Kate_M"][Math.floor(Math.random() * 8)];
var pos;
var room;

var geotext = document.getElementById("geo-text")
function getRoom() {
	console.log('Requesting position')
  if (navigator.geolocation) {
    pos = navigator.geolocation.getCurrentPosition(getClosestEntity);
		//console.log('Watching position')
    //navigator.geolocation.watchPosition(showPosition);
  } else {
    geotext.innerHTML = "Geolocation is not supported by this browser.";
  }
}

var redMarker = L.AwesomeMarkers.icon({
    prefix: 'fa',
    icon: 'bus',
    markerColor: 'red'
  });

function getClosestEntity(position) {
	fetch('https://3jaz6s2dul.execute-api.ap-southeast-2.amazonaws.com/dev/whoami?lat=' + position.coords.latitude + '&lon=' + position.coords.longitude)
	.then(res => res.json())
	.then(data => {
		console.log(data);
		window.transportEntity = data;
		room = data.label;
		setupWebSocket();

        map.flyTo([ data.lat, data.lon ], 13);
        L.marker([ data.lat, data.lon ],
                      { icon: redMarker, zIndex: 1000 })
             .addTo(map)
	})

  //geotext.innerHTML = "Latitude: " + position.coords.latitude +
  //"<br>Longitude: " + position.coords.longitude;
}

// Connect to the WebSocket and setup listeners
function setupWebSocket() {
    socket = new ReconnectingWebSocket("wss://7gig8cl05b.execute-api.ap-southeast-2.amazonaws.com/dev");

	  document.getElementById("header-text").innerHTML = "Welcome Aboard " + room + "!"
		if(transportEntity.dist > 50){document.getElementById("demo-text").innerHTML = "(we can see you're actually ~"+ (transportEntity.dist/1000).toFixed(2) +" km from a supported public transport vehicle, but for demo purposes we've pretended you're on the closest one!)"}
		document.getElementById("stop-text").innerHTML = "Your next stop is: " + transportEntity.rawData.stopInfo.stop_name + "."
	  socket.onopen = function(event) {
        data = {"action": "getRecentMessages", "room": room};
        // socket.send(JSON.stringify(data));

				setTimeout(function(){
					$("#message-container").append("<div class='message self-message text-center'>-----")
					$("#message-container").append("<strong><p>Welcome to T-Chat</p><p>It is Sunday 8 September at 07:15am.</p><p>The weather today is expected to be partially cloudy and rising from 2C now (brrr!) to 12C by 3pm. I hope you brought your coat!</p><p>You have joined T-chat as "+username+"</p></strong>")
				}, 6000);
				setTimeout(function(){
					$("#message-container").append("<div class='message self-message'><b>(@driver)</b> Welcome to T-Chat for the 7:17 am Rapid Service (route 2) to Belconnen, City and Fyshwick.")
				}, 10000);
				setTimeout(function(){
					$("#message-container").append("<div class='message self-message'><b>(@driver)</b> Four of your fellow travellers are using T-Chat right now.")
				}, 14000);
				setTimeout(function(){
					$("#message-container").append("<div class='message self-message'><b>(@driver)</b> Ask me if you have <strong>questions about our route and destinations</strong>, want an update on <strong>transport service delays</strong>, would like a <strong>tour</strong> along the route, or wish to <strong>play a game</strong> against another route. You can <strong>ask me</strong> what else I can help you with.")
					$("#message-container").append("<div class='message self-message text-center'>-----")
					$("#message-container").children().last()[0].scrollIntoView();
				}, 17000)
    };

	  socket.onmessage = function(message) {
        var data = JSON.parse(message.data);
				console.log(data)
        data["messages"].forEach(function(message) {
            if (message["username"] === username) {
                $("#message-container").append("<div class='message self-message'><b>(You)</b> " + message["content"]);
            } else {
                $("#message-container").append("<div class='message'><b>(" + message["username"] + ")</b> " + message["content"]);
            }
            $("#message-container").children().last()[0].scrollIntoView();
        });
    };
}

function postMessage() {
    var content = $("#post-bar").val();
		postMessageDirect(content, username)
		if (content.startsWith("@driver")){
				setTimeout(function(){respondToChat(content)}, 500)
		}
}

function postMessageDirect(content, username) {
	if (content !== "") {
			data = {"action": "sendMessage", "username": username, "content": content, "room": room};
			socket.send(JSON.stringify(data));
			$("#post-bar").val("");
	}
}

function respondToChat(content){
		if( wordCheck(content,["time","long","far"]) ){
			postMessageDirect("The next stop is 1 minute away", "@driver")
		}
		else if( wordCheck(content,["vehicle"]) ){
			postMessageDirect(room, "@driver")
		}
		else if( wordCheck(content,["near", "interesting"]) ){
			postMessageDirect("On your left is one of the oldest buildings in the region!", "@driver")
		}
		else if( wordCheck(content,["help"]) ){
			postMessageDirect("We're here to help. Your request has been noted and a human will get back to you shortly.", "@driver")
		}
		else if( wordCheck(content,["hello"]) ){
			postMessageDirect("Hello!", "@driver")
		}
		else if( wordCheck(content,["delays"]) ){
			postMessageDirect("No "+username+", the latest traffic report indicates that the route is <strong>clear and free flowing</strong>, we’ll have you at your destination in a jiffy!", "@driver")
		}
		else if( wordCheck(content,["usual driver"]) ){
			postMessageDirect("That’s right " + username +", we have upgraded our buses and your driver today is <strong>Joan</strong>. She has worked as a driver with us for <strong>seven years</strong>.", "@driver")
		}
		else if( wordCheck(content,["usual stop"]) ){
			postMessageDirect("Your usual stop is <strong>City Interchange</strong>. We expect to arrive at <strong>8:22am</strong>, but don't blame me for red lights!", "@driver")
		}
		else {
			postMessageDirect("I'm sorry, I couldn't understand your message. Please use the word 'help' if you would like a human to respond.", "@driver")
		}
}

function wordCheck(content, words){
	return words.some(function(word){
		return content.includes(word)
	})
}
