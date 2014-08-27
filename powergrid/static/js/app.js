
$(function() {
    var player = (function() {
	var setupWs = function() {
	    var l = window.location;
	    var ws_loc = "ws://" + l.hostname + ":" + l.port + "/ws";
	    return new WebSocket(ws_loc);
	},

	handle_newplayer = function(msg) {
	    $('#playerlist').append($('<li/>', {
		id: msg.body.name.replace(" ", "-"),
		text: " " + msg.body.name
	    }).addClass('player-'+msg.body.color));
	},

	handle_deadplayer = function(msg) {
	    $('#'+msg.body.name.replace(" ", "-")).remove();
	};

	handle_yourplayer = function(msg) {
	    $('#playerlist').append($('<li/>', {
		id: msg.body.name.replace(" ", "-"),
		text: ' (You) ' + msg.body.name
	    }).addClass('player-'+msg.body.color));
	}
	
	var ws = setupWs();
	ws.onopen = function() {
	    ws.send(JSON.stringify({"type": "CONNECT",
				    "body": ""}));
	};

	ws.onmessage = function(evt) {
	    var msg = JSON.parse(evt.data);
	    switch (msg.type) {
		case "NEWPLAYER":
		  handle_newplayer(msg);
		  break;
		case "DEADPLAYER":
		  handle_deadplayer(msg);
		  break;
		case "YOURPLAYER":
		  handle_yourplayer(msg);
		  break;
	    };
	    console.log(JSON.parse(evt.data));
	};

	return;
    })();
    
});
