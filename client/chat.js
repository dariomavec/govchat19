var socket;
var username = "client-" + Math.floor(Math.random() * 10000);
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

function getClosestEntity(position) {
	fetch('https://3jaz6s2dul.execute-api.ap-southeast-2.amazonaws.com/dev/whoami?lat=' + position.coords.latitude + '&lon=' + position.coords.longitude)
	.then(res => res.json())
	.then(data => {
		console.log(data);
		room = data.label;
		setupWebSocket();

        map.panTo([ position.coords.latitude, position.coords.longitude ]);
	})

  //geotext.innerHTML = "Latitude: " + position.coords.latitude +
  //"<br>Longitude: " + position.coords.longitude;
}

// Connect to the WebSocket and setup listeners
function setupWebSocket() {
    socket = new ReconnectingWebSocket("wss://7gig8cl05b.execute-api.ap-southeast-2.amazonaws.com/dev");

	  document.getElementById("header-text").innerHTML = "Welcome Aboard " + room + "!"
	  socket.onopen = function(event) {
        data = {"action": "getRecentMessages", "room": room};
        socket.send(JSON.stringify(data));
    };

	  socket.onmessage = function(message) {
        var data = JSON.parse(message.data);
				console.log(data)
        data["messages"].forEach(function(message) {
            if ($("#message-container").children(0).attr("id") == "empty-message") {
                $("#message-container").empty();
								window.flag = 1
            }
            if (message["username"] === username) {
                $("#message-container").append("<div class='message self-message'><b>(You)</b> " + message["content"]);
            } else {
                $("#message-container").append("<div class='message'><b>(" + message["username"] + ")</b> " + message["content"]);
            }
						if (window.flag === 1){
							setTimeout(function(){
							$("#message-container").append("<div class='message self-message text-center'>-----")
							$("#message-container").append("<strong><p>Welcome to T-Chat</p><p>It is Sunday 8 September at 07:15am.</p><p>The weather today is expected to be partially cloudy and rising from 2C now (brrr!) to 12C by 3pm. I hope you brought your coat!</p><p>You have joined T-chat as Jane_C</p></strong>")
							$("#message-container").append("<div class='message self-message'><b>(@driver)</b> Welcome to T-Chat for the 7:17 am Rapid Service (route 2) to Belconnen, City and Fyshwick.")
							$("#message-container").append("<div class='message self-message'><b>(@driver)</b> Four of your fellow travellers are using T-Chat right now.")
							$("#message-container").append("<div class='message self-message'><b>(@driver)</b> Ask me if you have <strong>questions about our route and destinations</strong>, want an update on <strong>transport service delays</strong>, would like a <strong>tour</strong> along the route, or wish to <strong>play a game</strong> against another route. You can <strong>ask me</strong> what else I can help you with.")
							$("#message-container").append("<div class='message self-message text-center'>-----")
							$("#message-container").children().last()[0].scrollIntoView();
						}, 300)
							window.flag=0
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
		if( wordCheck(content,["time","when","long","far"]) ){
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
		else {
			postMessageDirect("I'm sorry, I couldn't understand your message. Please use the word 'help' if you would like a human to respond.", "@driver")
		}
}

function wordCheck(content, words){
	return words.some(function(word){
		return content.includes(word)
	})
}
