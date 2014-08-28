
$(function() {
    var player = (function() {
    var pending_cities = [];
    var player_color = "";
    var button_submit = $('#btn-submit');
    var button_clear = $('#btn-clear');
    var button_change_color = $('#btn-change-color');
    var button_accept_color = $('#btn-choose-color');

	var setupWs = function() {
	    var l = window.location;
	    var ws_loc = "ws://" + l.hostname + ":" + l.port + "/ws";
	    return new WebSocket(ws_loc);
	};

	var handle_newplayer = function(msg) {
	    $('#playerlist').append($('<li/>', {
		id: msg.body.name.replace(" ", "-"),
		text: " " + msg.body.name
	    }).addClass('player-'+msg.body.color));
	};

	var handle_deadplayer = function(msg) {
	    $('#'+msg.body.name.replace(" ", "-")).remove();
	};

	var handle_yourplayer = function(msg) {
	    $('#color-modal').modal('hide');
	    $('#playerlist').children().first().remove();
	    $('#playerlist').prepend($('<li/>', {
		    id: msg.body.name.replace(" ", "-"),
		    text: ' (You) ' + msg.body.name
	        }).addClass('player-'+msg.body.color));
	    $('.house-'+player_color+'.interactable').removeClass('house-'+player_color).addClass('house-'+msg.body.color);
	    player_color = msg.body.color;

	};

	var handle_boardinfo = function(msg) {
	    $('#citylist').empty();
	    pending_cities = [];
	    update_pending_city_list();
	    var items = [];
	    $.each(msg.body.cities, function(i, item) {
	        var list_item = '<li class=\'city-'+item.region_color+'\'>';
	        var num_houses = item.houses.length;
	        var first_blank = true;
	        for (var i = 0; i < 3; i++) {
	            if (i < num_houses) {
	                list_item += '<div class=\'house-'+item.houses[i]+'\'>'+String(10+(i*5))+'</div>';
	            } else {
	                if (first_blank) {
	                    list_item += '<div class=\'house-blank-purchaseable interactable\'>'+String(10+(i*5))+'</div>';
	                } else {
	                    list_item += '<div class=\'house-blank\'>'+String(10+(i*5))+'</div>';
	                }
	                first_blank = false;
	            }
	        }
	        list_item += item.name+' ';
	        list_item += '</li>';
	        items.push(list_item);
	        var new_list_item = $(list_item)

	        var purchase = function(e) {
	            add_city(item.name);
	            $(this).removeClass('house-blank-purchaseable')
	                           .addClass('house-'+player_color)
	                           .unbind()
	                           .click(unpurchase);
	            e.preventDefault();
	        };

	        var unpurchase = function(e) {
	            remove_city(item.name);
	            $(this).removeClass('house-'+player_color)
	                           .addClass('house-blank-purchaseable')
	                           .unbind()
	                           .click(purchase);
	            e.preventDefault();
	        };

	        new_list_item.find('div.house-blank-purchaseable').click(purchase);
	        $('#citylist').append(new_list_item);

	    });
	};

	var add_city = function(city_name) {
	    pending_cities.push(city_name);
	    update_pending_city_list();
	};

	var remove_city = function(city_name) {
	    var index = pending_cities.indexOf(city_name);
	    if (index > -1) {
	        pending_cities.splice(index, 1);
	    }
	    update_pending_city_list();
	};


	var update_pending_city_list = function() {
	    pending_city_list = $('#pendinglist');
	    pending_city_list.empty()
	    $.each(pending_cities, function(i, item) {
	        pending_city_list.append($('<li>'+item+'</li>'));
	    });
	    get_cost();
	}


	var handle_costresult = function(msg) {
	    var cost = msg.body.cost;
	    var house = msg.body.houses;
	    var path = msg.body.paths;
	    $('#housecost').html("Houses: "+String(house));
	    $('#pathcost').html("Connection: "+String(path));
	    $('#cost').html("Total Cost: "+String(cost));
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
		case "BOARDINFO":
		  handle_boardinfo(msg);
		  break;
		case "COSTRESULT":
		  handle_costresult(msg);
		  break;
		case "PURCHASERESULT":
		  handle_purchaseresult(msg);
		  break;
		case "COLORSAVAILABLE":
		  handle_colorsavailable(msg);
		  break;
	    };
	    console.log(msg);
	};

    var get_cost = function() {
	    ws.send(JSON.stringify({"type": "COSTREQUEST",
	                            "body": {"player": player_color,
	                                     "cities": pending_cities}}));
	};

    var submit_purchase = function() {
        ws.send(JSON.stringify({"type": "PURCHASE",
                                "body": {"cities": pending_cities}}));
    }

    var handle_purchaseresult = function(msg) {
        if (msg.body.error != "") {
            console.log(msg.body.error);
        }
        pending_cities = [];
        update_pending_city_list();
    }

    button_submit.click(submit_purchase);

    var clear_board = function() {
        ws.send(JSON.stringify({"type": "CLEARBOARD",
                                "body": {}}));
        pending_cities = [];
        update_pending_city_list();
    }

    button_clear.click(clear_board);

    var change_color = function() {
        ws.send(JSON.stringify({"type": "REQUESTCOLORS",
                                "body": ""}));
    }

    button_change_color.click(change_color);

    var handle_colorsavailable = function(msg) {
        var first = true;
        $('#coloroptions').empty();
        $.each(msg.body, function(i, item) {
            var option = $("<option/>", {value: item}).text(item);
            if (first) {
                option.prop('selected', true);
            }
            $('#coloroptions').append($("<option\>", {value: item})
            .text(item));
        });
        $('#color-modal').modal('show');
    }

    var accept_color = function() {
        color_chosen = $("#coloroptions").val();
        if (!color_chosen) {
            $("#color-modal").modal('hide');
            return;
        }
        ws.send(JSON.stringify({"type": "CHANGECOLOR",
                                "body": color_chosen}))
    }

    button_accept_color.click(accept_color);

	return;
    })();
    
});
