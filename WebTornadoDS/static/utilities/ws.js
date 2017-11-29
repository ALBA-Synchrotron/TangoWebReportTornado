
$(document).ready(function() {
      $.ajaxSetup({ cache: false });

    updater.start();
});



var updater = {
    socket: null,

    start: function() {
        var url = "ws://" + location.host + "/service";
        updater.socket = new WebSocket(url);
        updater.socket.onmessage = function(event) {
            updater.dataReceived(JSON.parse(event.data));
        }
    },

    dataReceived: function(jsondata) {

        if (jsondata['command'] =='config'){
            start(jsondata);

        }else if (jsondata['command'] =='update'){
            updateValues(jsondata)
        }
    }
};

function sendCommand(command, value ) {
    var data = {}

    /****************************/
    /* Add fields here  to data */
    /****************************/
    data[command] = value;

    updater.socket.send(JSON.stringify(data));
};
