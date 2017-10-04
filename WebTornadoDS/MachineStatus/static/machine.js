// Array with lines urls and names

var lines = {};

lines.BL01 = {name: 'MIRAS', FEUrl:'sys/tg_test/1/boolean_scalar', idUrl: 'sys/tg_test/1/long64_scalar', FEname: 'BL01', idname: 'M1'}
lines.BL04 = {name: 'MSPD', FEUrl:'sys/tg_test/1/boolean_scalar', idUrl: 'sys/tg_test/1/long64_scalar', FEname: 'FE04', idname: 'SCW01'};
lines.BL09 = {name: 'MISTRAL', FEUrl:'sys/tg_test/1/boolean_scalar', idUrl: '', FEname: 'FE09', idname: 'BEND' };
lines.BL11 = {name: 'NCD', FEUrl:'sys/tg_test/1/boolean_scalar', idUrl: 'sys/tg_test/1/long64_scalar', FEname: 'FE11', idname: 'IVU21' };
lines.BL13 = {name: 'XALOC', FEUrl:'sys/tg_test/1/boolean_scalar', idUrl: 'sys/tg_test/1/long64_scalar', FEname: 'FE13', idname: 'IVU21' };
lines.BL22 = {name: 'CLAESS', FEUrl:'sys/tg_test/1/boolean_scalar', idUrl: 'sys/tg_test/1/long64_scalar', FEname: 'FE22', idname: 'MPW80' };
lines.BL24 = {name: 'CIRCE', FEUrl:'sys/tg_test/1/boolean_scalar', idUrl: 'sys/tg_test/1/long64_scalar', FEname: 'FE24', idname: 'EU62' };
lines.BL29 = {name: 'BOREAS', FEUrl:'sys/tg_test/1/boolean_scalar', idUrl: 'sys/tg_test/1/long64_scalar', FEname: 'FE29', idname: 'EU71' };

// Array with machine status like pressure, current, life time ...

var machinestatus = {};

machinestatus.Pressure = {name: 'Pressure', Url:'sys/tg_test/1/double_scalar'};
machinestatus.LifeTime = {name: 'Lifetime', Url:'sys/tg_test/1/double_scalar'};
machinestatus.Current = {name: 'Current', Url:'sys/tg_test/1/double_scalar'};
machinestatus.Message = {name: 'usermessage', Url:'sys/tg_test/1/string_scalar'};
machinestatus.Data = {name: 'Data', Url:'sys/tg_test/1/double_scalar'};
machinestatus.Product = {name: 'Product', Url:'sys/tg_test/1/long64_scalar'};

var plot_Url='sys/tg_test/1/double_spectrum_ro';

// Variables for the periods refresh

var set_refreshjson_period = 5000;
var set_refreshplot_period = 10000;

var data_tmp = '';
var plot_data;

// Plot configuarations and options

var plot_options = {
                  title: {
                    text:'Current',
                    fontSize:'20pt'
                  },

                  height: 400,                          // Define the height of the plot
                  width: 400,                           // Define the width of the plot
                  axes:{
                    xaxis:{
                      renderer:$.jqplot.DateAxisRenderer,
                      tickRenderer: $.jqplot.CanvasAxisTickRenderer,
                      tickOptions:{
                        formatString:'%b %#d, %#I %p',  // Define the format of the axis of X
                        tickInterval:'3',
                        fontSize: '12pt',               // Define the size of the text
                        angle: -45                      // Define the angle of the position of the text in the axis X

                        }
                    },
                    yaxis:{
           ticks: ['0','20','40','60','80','100','120','140','160'],  // Define the values of the axis of Y
                    label:'mA',
           min:0,
                    labelRenderer: $.jqplot.CanvasAxisLabelRenderer,  // Define the format for the text on the label
                    labelOptions:{
            formatString : '%.2f',
                        fontSize: '22pt'
                    },
                    tickRenderer: $.jqplot.CanvasAxisTickRenderer,  // Define the format for the text on the axis Y
                    tickOptions:{
            formatString : '%.2f',
                        fontSize: '18pt'
                      }

                    }
                  },
                                  series:[
                {                                   // Define the format (colors, style ...) of the plot
                lineWidth:4,
                color:'red', //#ff0000
                showMarker:false,
                fill: true,
                fillAndStroke: true,
                fillColor:'#ff0000',
                fillAlpha: 0.4,
          markerOptions: { style:'diamond' }
                }],

                grid: {                     // Define the "Grid", in this case we have a black background
                  drawGridLines: false,
                  background: "black",
                  shadow: false
                },
              };

// Load the image of the alba logo

var settime = 0;
var img = new Image();          // Creation of the object who contain the alba image
//img.src = "AlbaLogo.png";   // Define the rute of the image
var URL_request = '';           // Initialization of the variable
var URL = '';                   // Initialization of the variable
var value = '';                 // Initialization of the variable
var refreshDate = '';           // Initialization of the variable

var tester = false;
var tester2 = false;
var tester3 = false;
var tester4 = false;
var tester5 = false;
var tester6 = false;
var tester7 = false;

// Creation of plot array without any data

var data = [];                  // Initialization of the variable data for the plot
var plot ;                      // Initialization of the variable plot for first time.

// Function for the creation of the beam structure. This function are doing and printing : the text of the name, the text of the FE, and the values of this variables.

function setLine(data,value,name,frontend,url){     // We have 4 variables:
                                                    // DATA: data is the data from Json File.
    $(name).text(URL.name);                         // VALUE: the value is the variable who define the where go the data of the Line
    $(frontend).text(URL.FEname);                   // NAME: Is the name of the line
    $(value).text(data); // FRONTEND: This variable is the name of the FE of the Lane
    if (data=="OPEN") {
        $(value).css("background-color", "Lime");   // URL: is the URL who identifies the line
    }
    else {
        $(value).css("background-color", "Orange");   // URL: is the URL who identifies the line
    }
}

// This Fucntion is used for change the color of text, this color depend of the bacground color.

function setColor(data,valueline){

    if (data == "OPEN"){
        $(valueline).css("color", 'black');    // Change the color to black when the value is Lime
    }else{
        $(valueline).css("color", 'white');    // Change the color to white when the value is other diferent to Lime
}



};

function createTooltip(site, error){

            var span = document.createElement("span");
            var a = document.createElement("a");

            a.className = "tooltips";
            a.textContent = "...";
            span.textContent = error.string;
            a.appendChild(span);

            document.getElementById(site).appendChild(a);

};

function createTooltipUP(site, error){

            var span = document.createElement("span");
            var a = document.createElement("a");

            a.className = "tooltips2";
            a.textContent = "...";
            span.textContent = error.string;
            a.appendChild(span);

            document.getElementById(site).appendChild(a);

};


// Creation of GUI whit the starts fresh periods
// Javascript function for refresh and load the data of the json

function refresh(datos){
    try{
        URL_request = machinestatus.Current.Url;                        // variable for pass the url of current

        data_tmp = String(Math.abs(datos["data"][String(URL_request)]["value"].toFixed(2)));
        $('#currentvalue').text(data_tmp + "  mA");    // Take the value of the current from the Json file and put it with " mA"
        $('#current').text(machinestatus.Current.name);                 // Put the text "Current" in the GUI

        URL_request = machinestatus.LifeTime.Url;                       // Variable for pass the url of Life Time

        data_tmp = String(Math.abs(datos["data"][String(URL_request)]["value"].toFixed(2)));

        $('#lifetime').text(machinestatus.LifeTime.name);               // Put the text "Lifetime" in the GUI
        $('#lifetimevalue').text(data_tmp);            // Take the value of the Life Time from the Json file

        URL_request = machinestatus.Product.Url;                        // Variable for pass the url of Product
        data_tmp = String(Math.abs(datos["data"][String(URL_request)]["value"].toFixed(2)));

        $('#product').text("("+ data_tmp + ")");       // Take the value of the "Product" from the Json file and put it inside of "()"

        URL_request = machinestatus.Pressure.Url;                       // Variable for pass the url of Pressure
        data_tmp = String(Math.abs(datos["data"][String(URL_request)]["value"].toFixed(2)));

        $('#pressure').text(machinestatus.Pressure.name);               // Put the text "Pressure" in the GUI
        $('#pressurevalue').text(data_tmp + " mbar");  // Take the value of the "Product" from the Json file and put it with " mbar"

        //Beamline MIRAS and all values

        URL_request = lines.BL01.FEUrl;                                 // Variable for pass the url of the FE of the lane
        URL = lines.BL01;                                               // Variable for pass the url of the lane
        value = '#FI03value';                                           // Varible with id of the FI value
        name = '#MIRAS';                                                // Id variable with name of the lane
        frontend = '#FI03';
        data_tmp = "OPEN";// Variable with id of the Frontend value
        if (String(datos["data"][String(URL_request)]["value"]) != "true") {
            data_tmp = "CLOSE";
        }

        setLine(data_tmp,value,name,frontend,URL);            // call to the function setLine
        setColor(data_tmp,value);                             // call to the function setColor

        URL_request = lines.BL01.idUrl;                                 // Variable for pass the url of the FI of the lane
        var value_instance = 'FI03POSvalue';

        $('#FI03POS').text(lines.BL01.idname);                          // Variable with the name of FI position
        data_tmp = String(Math.abs(datos["data"][String(URL_request)]["value"].toFixed(2)));

        if ((data_tmp).length > 11){

            var console_message = data_tmp;

            if(tester == false){
                createTooltip(value_instance, datos[URL_request] );
                console.log(console_message);
                tester = true;
            }
        }else{
            $('#FI03POSvalue').text(data_tmp);         // Take the value of the "Position of FI" from the Json file
            tester = false;
        }
        if (String(datos["data"][String(URL_request)]["quality"]) == "ATTR_VALID") {
            $('#FI03POSvalue').css("background-color", "Lime");
        }
        else {
            $('#FI03POSvalue').css("background-color", "Orange");
        }

        //Beamline MSPD and all values ---> This part have the same estructure than Miras beamline

        URL_request = lines.BL04.FEUrl;
        URL = lines.BL04;
        value = '#FE04value';
        name = '#MSPD';
        frontend = '#FE04';
        data_tmp = "OPEN";// Variable with id of the Frontend value
        if (String(datos["data"][String(URL_request)]["value"]) != "true") {
            data_tmp = "CLOSE";
        }

        setLine(data_tmp,value,name,frontend,URL);            // call to the function setLine
        setColor(data_tmp,value);                             // call to the function setColor


        URL_request = lines.BL04.idUrl;
        var value_instance = 'SCW01value';


        $('#SCW01').text(lines.BL04.idname);
        data_tmp = String(Math.abs(datos["data"][String(URL_request)]["value"].toFixed(2)));

        if ((data_tmp).length > 6){

            var console_message = data_tmp;
            if(tester2 == false){
                createTooltip(value_instance, datos[URL_request] );
                console.log(console_message);
                tester2 = true;
            }

        }else{
        $('#SCW01value').text("B = "+data_tmp+" T");
            tester2 = false;
        }
        if (String(datos["data"][String(URL_request)]["quality"]) == "ATTR_VALID") {
            $('#SCW01value').css("background-color", "Lime");
        }
        else {
            $('#SCW01value').css("background-color", "Orange");
        }


        // Beamline Mistral and all values  ---> This part have the same estructure than Miras beamline

        URL_request = lines.BL09.FEUrl;
        URL = lines.BL09;
        value = '#FE09value';
        name = '#MISTRAL';
        frontend = '#FE09';
        data_tmp = "OPEN";// Variable with id of the Frontend value
        if (String(datos["data"][String(URL_request)]["value"]) != "true") {
            data_tmp = "CLOSE";
        }

        setLine(data_tmp,value,name,frontend,URL);            // call to the function setLine
        setColor(data_tmp,value);                             // call to the function setColor


        $('#BEND').text(lines.BL09.idname);
        $('#BEND').text(lines.BL09.idname);


        // Beamline NCD and all values ---> This part have the same estructure than Miras beamline

        URL_request = lines.BL11.FEUrl;
        URL = lines.BL11;
        value = '#FE11value';
        name = '#NCD';
        frontend = '#FE11';
        data_tmp = "OPEN";// Variable with id of the Frontend value
        if (String(datos["data"][String(URL_request)]["value"]) != "true") {
            data_tmp = "CLOSE";
        }

        setLine(data_tmp,value,name,frontend,URL);            // call to the function setLine
        setColor(data_tmp,value);                             // call to the function setColor

        URL_request = lines.BL11.idUrl;
        var value_instance = 'IVU21value';

        $('#IVU21').text(lines.BL11.idname);
        data_tmp = String(Math.abs(datos["data"][String(URL_request)]["value"].toFixed(2)));

        if ((data_tmp).length > 6){
             var console_message = data_tmp;
            if(tester3 == false){
                createTooltip(value_instance, datos[URL_request] );
                console.log(console_message);
                tester3 = true;
            }
        }else{
        $('#IVU21value').text(data_tmp + " mm");
            tester3 = false;
        }
        if (String(datos["data"][String(URL_request)]["quality"]) == "ATTR_VALID") {
            $('#IVU21value').css("background-color", "Lime");
        }
        else {
            $('#IVU21value').css("background-color", "Orange");
        }

        // Beamline Xaloc and all values ---> This part have the same estructure than Miras beamline

        URL_request = lines.BL13.FEUrl;
        URL = lines.BL13;
        value = '#FE13value';
        name = '#XALOC';
        frontend = '#FE13';
        data_tmp = "OPEN";// Variable with id of the Frontend value
        if (String(datos["data"][String(URL_request)]["value"]) != "true") {
            data_tmp = "CLOSE";
        }

        setLine(data_tmp,value,name,frontend,URL);            // call to the function setLine
        setColor(data_tmp,value);                             // call to the function setColor


        URL_request = lines.BL13.idUrl;
        value_instance = 'IVU21_2value';

        $('#IVU21_2').text(lines.BL13.idname);
        data_tmp = String(Math.abs(datos["data"][String(URL_request)]["value"].toFixed(2)));

        if ((data_tmp).length > 6){
             var console_message = data_tmp;
            if(tester4 == false){
                createTooltip(value_instance, datos[URL_request] );
                console.log(console_message);
                tester4 = true;
            }
        }else{
        $('#IVU21_2value').text(data_tmp + " mm");
            tester4 = false;
        }
        if (String(datos["data"][String(URL_request)]["quality"]) == "ATTR_VALID") {
            $('#IVU21_2value').css("background-color", "Lime");
        }
        else {
            $('#IVU21_2value').css("background-color", "Orange");
        }

        // BeamLine CLaess and all values ---> This part have the same estructure than Miras beamline

        URL_request = lines.BL22.FEUrl;
        URL = lines.BL22;
        value = '#FE22value';
        name = '#CLAESS';
        frontend = '#FE22';
        data_tmp = "OPEN";// Variable with id of the Frontend value
        if (String(datos["data"][String(URL_request)]["value"]) != "true") {
            data_tmp = "CLOSE";
        }

        setLine(data_tmp,value,name,frontend,URL);            // call to the function setLine
        setColor(data_tmp,value);                             // call to the function setColor


        URL_request = lines.BL22.idUrl;
        value_instance = 'MPW80value';

        $('#MPW80').text(lines.BL22.idname);
        data_tmp = String(Math.abs(datos["data"][String(URL_request)]["value"].toFixed(2)));

        if ((data_tmp).length > 6){
             var console_message = data_tmp;
            if(tester5 == false){
                createTooltipUP(value_instance, datos[URL_request] );
                console.log(console_message);
                tester5 = true;
            }
        }else{
        $('#MPW80value').text(data_tmp + " mm");
        tester5 = false;
        }
        if (String(datos["data"][String(URL_request)]["quality"]) == "ATTR_VALID") {
            $('#MPW80value').css("background-color", "Lime");
        }
        else {
            $('#MPW80value').css("background-color", "Orange");
        }

        // Beamline Circe and all values ---> This part have the same estructure than Miras beamline

        URL_request = lines.BL24.FEUrl;
        URL = lines.BL24;
        value = '#FE24value';
        name = '#CIRCE';
        frontend = '#FE24';
        data_tmp = "OPEN"// Variable with id of the Frontend value
        if (String(datos["data"][String(URL_request)]["value"]) != "true") {
            data_tmp = "CLOSE";
        }

        setLine(data_tmp,value,name,frontend,URL);            // call to the function setLine
        setColor(data_tmp,value);                             // call to the function setColor

        URL_request = lines.BL24.idUrl;
        value_instance = 'EU62value';

        $('#EU62').text(lines.BL24.idname);
        data_tmp = String(Math.abs(datos["data"][String(URL_request)]["value"].toFixed(2)));

        if ((data_tmp).length > 6){
             var console_message = data_tmp;
            if(tester6 == false){
                createTooltipUP(value_instance, datos[URL_request] );
                console.log(console_message);
                tester6 = true;
            }
        }else{
        $('#EU62value').text(data_tmp + " mm");
        tester6 = false;
        }
        if (String(datos["data"][String(URL_request)]["quality"]) == "ATTR_VALID") {
            $('#EU62value').css("background-color", "Lime");
        }
        else {
            $('#EU62value').css("background-color", "Orange");
        }

        // Beamline Boreas and all values ---> This part have the same estructure than Miras beamline

        URL_request = lines.BL29.FEUrl;
        URL = lines.BL29;
        value = '#FE29value';
        name = '#BOREAS';
        frontend = '#FE29';
        data_tmp = "OPEN"; // Variable with id of the Frontend value
        if (String(datos["data"][String(URL_request)]["value"]) != "true") {
            data_tmp = "CLOSE";
        }

        setLine(data_tmp,value,name,frontend,URL);            // call to the function setLine
        setColor(data_tmp,value);                             // call to the function setColor

        URL_request = lines.BL29.idUrl;
        value_instance = 'EU71value';

        $('#EU71').text(lines.BL29.idname);
        data_tmp = String(Math.abs(datos["data"][String(URL_request)]["value"].toFixed(2)));

        if ((data_tmp).length > 6){
              var console_message = data_tmp;
            if(tester7 == false){
                createTooltipUP(value_instance, datos[URL_request] );
                console.log(console_message);
                tester7 = true;
            }
        }else{
        $('#EU71value').text(data_tmp + " mm");
        tester7 = false;
        }
        if (String(datos["data"][String(URL_request)]["quality"]) == "ATTR_VALID") {
            $('#EU71value').css("background-color", "Lime");
        }
        else {
            $('#EU71value').css("background-color", "Orange");
        }

        //Data and Machines status valuesing

        URL_request = machinestatus.Data.Url;                               // Variable for pass the url of the Data

        value = '#usertext';                                                // Is the variable for  pass the id form the Htm

        var dt = new Date()
        var d = dt.toDateString();
        var h = dt.getHours();
        var mi = ('0'+dt.getMinutes()).slice(-2);
        var s = ('0'+dt.getSeconds()).slice(-2)

        data_tmp =d+"   "+h+":"+mi+":"+s;
        $('#data').text(data_tmp);                         // This take the value of data and put in GUI

        URL_request = machinestatus.Message.Url;                           // Variable for pass the url of the User_Text of the machine

        stringmessage = String(datos["data"][String(URL_request)]["value"]);

        if ((stringmessage.startsWith('<') == true) && (stringmessage.endsWith('>') == true)) {
            //embed raw text as html
            $('#usertext').html(stringmessage); // String who contain the user texct message
        } else {
            $('#usertext').text(stringmessage);                     // String who contain the user texct message
            if (String(datos["data"][String(URL_request)]["quality"]) == "ATTR_VALID") {
                $('#usertext').css("background-color", "Lime");
                $('#usertext').css("color", 'black');    // Change the color to black when the value is Lime
            }
            else {
                $('#usertext').css("background-color", "Orange");
                $('#usertext').css("color", 'white');    // Change the color to black when the value is Lime
            }
        }

        if (plot) {
            plot.destroy();                // The destroy metod, delete our actual graphic
        }
        URL_request = plot_Url;
        plot_data = datos["data"][String(URL_request)]["value"]
        console.log(plot_data);
        plot = $.jqplot ('chart3', [plot_data], plot_options); // Creation of the plot again, but with the new data


      }catch(err) {
          console.log(err);

      }

 }


$(document).ready(function() {
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
            refresh(jsondata);
            console.log("INICIO")

        }else if (jsondata['command'] =='update'){
            ///updateValues(jsondata)
            ///doUpdate();
            refresh(jsondata);
            console.log("REFRESH")
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
