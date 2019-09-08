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
            }
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
    if (content !== "") {
        data = {"action": "sendMessage", "username": username, "content": content, "room": room};
        socket.send(JSON.stringify(data));
        $("#post-bar").val("");
    }
}
