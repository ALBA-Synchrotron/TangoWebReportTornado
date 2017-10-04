
var myCharts = {};
var structure_config;

function start(jsondata){
            structure_config = jsondata;
            var keys = [];
            var key;
	    createFormStructure();

            for (key in jsondata.config){
                var data = jsondata.config[key];
                createTableFromList(data, jsondata, key);
            }
            jsondata = null;

}

// Function for  iterate a list of attributes, and pass to the other functions

function createTableFromList(config, jsondata, key){

/* Here there are the substitute of the special characters, like the character "_"
with the same variable without this char, this process will create other variable
used like id. In the case of IDTitle, substitute the same name but with upper
characters.*/
    var idDiv =  extractFileName(key);
    var idTitle = key.toUpperCase()+"id";


    createIndex(key, idTitle);
    /*This lane was cometed cause this function is incomplete*/
    //createLoadInfo();
    createHeadland(key, idDiv, idTitle, config.Description, config.Status);



    var dataJson =  jsondata.data;

    var plot_type = false;
    var histFile;

    for (var i=0; i<config.Data.length; i++) {

        if (config.Data[i].length > 0){
                var at = config.Data[i];
                if( dataJson[at.toLowerCase()].data_format != "SCALAR" ){
                    plot_type = true;
                    histFile = config.Data[i];
                }
            var section_Name = key.replace(/\ /g,"");
            createTable(config.Data[i], dataJson, section_Name, plot_type, histFile);
            plot_type = false;

         }
    }
}


/*Get the name of the file from the title name*/

function extractFileName(Title){

    var title_name = Title.replace(/[&\/\\#,+()$~%.'":*?<>{}]/g, "");
    var valor = title_name;
    var fileName = valor.replace(/\ /g,"");


 return fileName;

}

// This function create actuamticaly the index of the top.

function createIndex(section_name, idTitle){

/*The var "exist" is used to check if the div with the structure of the index,
it is created or not. If it is equal to 0, It will be created the estructure
of the index.*/

    var exist = document.getElementsByClassName("jumbotron").length;

    if(exist == 0){

        // Creation the structure of the Index
        var divIndex_Structure_Content = document.createElement("div");
        var divIndex_List = document.createElement("div");
        var ul_Index = document.createElement("ul");
        document.getElementById("content").appendChild(divIndex_Structure_Content);

        divIndex_Structure_Content.className = "jumbotron";
        divIndex_Structure_Content.appendChild(divIndex_List);
        divIndex_List.className = "list-group";
        divIndex_List.appendChild(ul_Index);
        ul_Index.id = "index";

    }

    // Creation of the Index
    var li_Index = document.createElement("li");
    var a_link_Index = document.createElement("a");
    var text = document.createTextNode(section_name);
    var txtForExpand = section_name + "_Down";
    document.getElementById("index").appendChild(li_Index);
    li_Index.appendChild(a_link_Index);
    a_link_Index.className = "list-group-item";
    a_link_Index.setAttribute("href", "#"+idTitle);
    a_link_Index.appendChild(text);
    a_link_Index.setAttribute("onclick","return expand('"+txtForExpand+"')");

}


/* This function create the HeadLand of the web reports, idDiv is the id and the
site for the table. title_name and idTitle are the names for the differents html
sections.*/

function createHeadland(section_name, idDiv, idTitle, Description, status){

    // Here are created the vars for the structure

    var div_headLand = document.createElement("div");
    var div_bttn_title = document.createElement("div");
    var div_table_deviceValues = document.createElement("div");
    var header_title = document.createElement("h3");
    var buttonDropdown = document.createElement("button");
    var span_title = document.createElement("span");
    var model_titleTxt = document.createTextNode(section_name + " ");

    var buttonEdit = document.createElement("button");
    var txtEdit = document.createTextNode("Edit");
    

    var header_Description = document.createElement("p");
    var txtDescription = document.createTextNode(Description);
    var boxStatus = document.createElement("div");

    // Structure implementation

    document.getElementById("content").appendChild(div_headLand);
    div_headLand.className = "panel panel-default";
    div_headLand.appendChild(div_bttn_title);
    div_bttn_title.className = "panel-heading";
    div_bttn_title.appendChild(header_title);
    
    boxStatus.className = "alert alert-info";
    boxStatus.setAttribute("role", "alert");
    boxStatus.innerHTML= "Not Updated";
    boxStatus.id = section_name+'_state'
    div_headLand.appendChild(boxStatus);
    header_title.id = idTitle;                                           
    header_title.className ="panel-title";                           
    header_title.appendChild(model_titleTxt);                                 
    header_title.appendChild(buttonDropdown);                                            
    buttonDropdown.className = "btn btn-default btn-sm";           
    buttonDropdown.setAttribute("type", "button");                 
    buttonDropdown.setAttribute("aria-label", "Left Align");       
    buttonDropdown.setAttribute("data-toggle", "collapse");        
    buttonDropdown.setAttribute("data-target", "#" + idDiv);
    buttonDropdown.id =idDiv + "_Down";        
    buttonDropdown.setAttribute("onclick", "");
                   
    buttonDropdown.appendChild(span_title);                              
    span_title.className = "glyphicon glyphicon-sort";          
    span_title.setAttribute("aria-hidden","true");              
    div_headLand.appendChild(div_table_deviceValues);                               
    div_table_deviceValues.id = idDiv;                                 
    div_table_deviceValues.className = "panel-collapse collapse in";
        
    div_table_deviceValues.setAttribute("height", "auto");


    div_table_deviceValues.appendChild(header_Description);
    header_Description.appendChild(txtDescription);
    header_Description.setAttribute("display", "inline");
    header_Description.setAttribute("style", "margin: 10px 20px;");
    header_Description.className ="separated";

    var idDescription = idDiv + "Des";

    header_Description.id = idDescription;

    // Button edit implementation

    var id_button = section_name.concat("_Button");   

    header_title.appendChild(buttonEdit);           
    buttonEdit.className = "btn btn-primary btn-sm pull-right";         
    buttonEdit.id = id_button;          
    buttonEdit.setAttribute("type", "button");                          
    buttonEdit.setAttribute("data-toggle", "modal");            
    buttonEdit.setAttribute("data-target", "#myModal");         
    buttonEdit.appendChild(txtEdit);
    buttonEdit.setAttribute("onclick", "getOutput('"+section_name+"');"); 
}

/*Thsi fucntion create the form structure of the web, the form was put in hidden
 * for don't disturve adn we can activate it with the new or edit buttons*/
function createFormStructure(){

        var title =  document.getElementById("first_Title");
        title.innerHTML= structure_config.host;
        
        
        // Check if exist or not a previous modal.

        var exist = document.getElementById("myModal");  
        
        if(exist == null){ 

            var div_modalContent = document.createElement("div");
            var div_modalDialog = document.createElement("div");
            var div_modalInside = document.createElement("div");
            var div_modalHeader = document.createElement("div");

            var form_tag = document.createElement("form");

            var button_closeModal = document.createElement("button");
            var span_closeX = document.createElement("span");

            var modalTitleLabel = document.createElement("label");
            var modalTitleContent = document.createElement("input");
            var hiddenModalTitleContent = document.createElement("input");

            var div_modalBody = document.createElement("div");
            var div_modalFooter = document.createElement("div");

            var label_sectionDescription = document.createElement("label");
            var input_sectionDescription = document.createElement("input");
            var txt_sectionDescription = document.createTextNode("Section Description:");

            var label_content = document.createElement("label");
            var textarea_content = document.createElement("textarea");
            var txt_content = document.createTextNode("Attributes:");

            var buttonDiscard = document.createElement("button");
            var textDiscard = document.createTextNode("Cancel");
            var buttonDelete = document.createElement("button");
            var textDelete = document.createTextNode("Delete");
            var buttonSave = document.createElement("button");
            var textSave = document.createTextNode("Save changes");

/*
            var hidden_pathInput = document.createElement("input");
*/



            document.getElementById("content").appendChild(form_tag);

            form_tag.id  = "formId";
            form_tag.setAttribute("action","");

            form_tag.appendChild(div_modalContent);

            div_modalContent.className = "modal fade";
            div_modalContent.id = "myModal";
            div_modalContent.setAttribute("tabindex","-1");
            div_modalContent.setAttribute("role","dialog");
            div_modalContent.setAttribute("aria-labelledby","title_label_modal");

            div_modalContent.appendChild(div_modalDialog);
            div_modalDialog.className = "modal-dialog";
            div_modalDialog.setAttribute("role","document");

            div_modalDialog.appendChild(div_modalInside);
            div_modalInside.className = "modal-content";

            div_modalInside.appendChild(div_modalHeader);
            div_modalHeader.className = "modal-header";

            div_modalHeader.appendChild(button_closeModal);
            button_closeModal.className = "close";
            button_closeModal.setAttribute("type","button");
            button_closeModal.setAttribute("data-dismiss","modal");
            button_closeModal.setAttribute("aria-label","Close");

            button_closeModal.appendChild(span_closeX);
            span_closeX.setAttribute("aria-hidden","true");
            span_closeX.innerHTML = '&times;';

            div_modalHeader.appendChild(modalTitleLabel);
            modalTitleLabel.className = "control-label";
            modalTitleLabel.setAttribute("for","title_label_modal");
            modalTitleLabel.innerHTML = ' Title: &nbsp';


            div_modalHeader.appendChild(modalTitleContent);
            modalTitleContent.className = "input-lg";
            modalTitleContent.id = "title_label_modal";
            modalTitleContent.setAttribute("name","Title");
            modalTitleContent.setAttribute("required","required");

            modalTitleContent.setAttribute("align", "center");

            div_modalHeader.appendChild(hiddenModalTitleContent);
            hiddenModalTitleContent.style.display = 'none';
            hiddenModalTitleContent.id = "hidden_title_label_modal";


            div_modalInside.appendChild(div_modalBody);
            div_modalBody.className = "modal-body";

/*            div_modalBody.appendChild(hidden_pathInput);
            hidden_pathInput.className = "form-control";
            hidden_pathInput.id = "path";
            hidden_pathInput.value = location.pathname;
            hidden_pathInput.setAttribute("name","path");
            document.getElementById("path").style.display = "none";*/

            div_modalBody.appendChild(label_sectionDescription);
            label_sectionDescription.className = "control-label";
            label_sectionDescription.setAttribute("for","description_label_modal");
            label_sectionDescription.appendChild(txt_sectionDescription);

            div_modalBody.appendChild(input_sectionDescription);
            input_sectionDescription.id ="description_label_modal";
            input_sectionDescription.className = "form-control";
            input_sectionDescription.setAttribute("name","Description");
            input_sectionDescription.setAttribute("type", "text");
            input_sectionDescription.setAttribute("required","required");

            div_modalBody.appendChild(label_content);
            label_content.className = "control-label";
            label_content.setAttribute("for","attrs_label_modal");
            label_content.appendChild(txt_content);

            div_modalBody.appendChild(textarea_content);
            textarea_content.className = "form-control";
            textarea_content.setAttribute("name","Data");
            textarea_content.id = "attrs_label_modal";
            textarea_content.setAttribute("required","required");


            div_modalInside.appendChild(div_modalFooter);
            div_modalFooter.className = "modal-footer";

            div_modalFooter.appendChild(buttonDiscard);
            buttonDiscard.className = "btn btn-warning";
            buttonDiscard.setAttribute("type","button");
            buttonDiscard.setAttribute("data-dismiss","modal");
            buttonDiscard.setAttribute("aria-label","Close");


            buttonDiscard.appendChild(textDiscard);

            div_modalFooter.appendChild(buttonDelete);
            buttonDelete.className = "btn btn-danger";
            buttonDelete.setAttribute("type","button");
            buttonDelete.setAttribute("onclick","deleteSection()");
            buttonDelete.id = "Delete";

            buttonDelete.appendChild(textDelete);

            div_modalFooter.appendChild(buttonSave);
            buttonSave.className = "btn btn-success";
            buttonSave.setAttribute("onclick","save()");
            buttonSave.appendChild(textSave);

	    }
	    
	    $('#myModal').on('hidden.bs.modal', function (e) {
		$(this)
		.find("input,textarea,select")
		   .val('')
		   .end()
		.find("input[type=checkbox], input[type=radio]")
		   .prop("checked", "")
		   .end();

	    document.getElementById("title_label_modal").removeAttribute("readonly");
	    document.getElementById("title_label_modal").setAttribute("required","required");


	    });
}

/* This function send the data of the "form", to the edit.php where this data 
will proceesed this data. When edit.php finish send and respons to save 
function, for print it and it inform to the user.*/

function save(){
      var des = document.getElementById('description_label_modal').value;
      var section = document.getElementById('title_label_modal').value;
      var prev_section = document.getElementById('hidden_title_label_modal')
      .value;

      var content = document.getElementById('attrs_label_modal').value;
      var conf = structure_config.config;
      // Delete the prev section name in the local configuration

      delete conf[prev_section]

      conf[section] = {};
      // Filtering the entry attr text, split, lowercase, etc...
      content = content.toLowerCase()
      content = content.split("\n");
      content = content.map(function (e) {return e.trim(); });
      
      content = content.filter(Boolean);
      conf[section].Data= content;
      conf[section].Description = des;
      var data = {};
      data.SaveNewConfig = conf;

      //console.log(data);
      updater.socket.send(JSON.stringify(data));
      //console.log('send!');
}

/* DeletFile is used for delete one element, this function to call the Delete
.php file and send the data of the element to delete. This funcion return an answer
 when finish the process with the result of the delete.*/

function deleteSection(){

    if(confirm("Are you sure you want to delete this Section?")) {

        var query = $('#formId').serialize();
        var section = document.getElementById('title_label_modal').value;
        var conf = structure_config.config;
        delete conf[section];
        var data = {};
        data.SaveNewConfig = conf;
        updater.socket.send(JSON.stringify(data));
        console.log('deleted!');
        location.reload()
    }
}


// Function javascript that returns the model without special chars

function cleanString(model){

    //delete special char from model string
    model = model.replace(/\//g,"-");
    model = model.replace(/\:/g,"-");
    model = model.replace(/\./g,"-");
    model = model.toLowerCase()
    return model;
}

// Create the name of the label site with the attribute
function createLabelName(Attr){

    var splittedAttr = Attr.split("/");
    var finalName = splittedAttr.pop();
    finalName = finalName.replace(/\.hist/g,"");    

    return finalName;
}

// Javascript function for create Table with attribut states

function createTable(Attr, json, title_name, plot_type, hist_File){
            var low  = Attr.toLowerCase();

            //Default variables  
            if ((json[low]) || (plot_type === true)) {

                var label;
                var model;
                var hist_NameFile;
                var modelo;
                if(plot_type === true){
                  
                    modelo = cleanString(Attr) ;
                    // Text for Element th 1, contains the attribute name
                    label = document.createTextNode(createLabelName(Attr)); 
                    hist_NameFile = hist_File;
                    // Text for Element th 1, contains the attribute name 
                    model = document.createTextNode(Attr); 

                }else{
                    Attr = low;
                    // Model of the attribute to add
                    modelo = cleanString(json[Attr].full_name);
                    // Text for Element th 1, contains the attribute name
                    label = document.createTextNode(json[Attr].label); 
                    model = document.createTextNode(json[Attr].full_name);
                     // Text for Element th 1, contains the attribute name
                }                

                
                var table = document.createElement("table");  
                var contentTable = document.createElement("tr");          
                var table_forLabel = document.createElement("th");            
                var table_forModalid = document.createElement("th");       
                var element_Br = document.createElement("br");        
                var span_forModal = document.createElement("span");   
                
                //Adding values                
                document.getElementById(title_name).appendChild(table);
                table.className = "separated";
                table_forLabel.appendChild(label);             
                table_forLabel.appendChild(element_Br);
                table_forLabel.appendChild(span_forModal);
                table_forLabel.style.width = "30%";
                span_forModal.style.align = "center";
                span_forModal.style.color = "grey";
                span_forModal.appendChild(model);
                var tit = cleanString(title_name);
                var id= tit+'_'+modelo;
                table_forModalid.id = id;
                table_forModalid.style.textAlign="center";                         
                table.appendChild(contentTable);              
                contentTable.appendChild(table_forLabel);                
                contentTable.appendChild(table_forModalid);                



                if( plot_type === true){
                    Plot(id, Attr);
                }

                if(json[low]){ 

                    /* Loop for check the quality of the attribute and change 
                    the color of the background
                     Here is checked the data format and if it is "SCALAR".*/
                     
                    if (json[Attr].data_format == "SCALAR"){                  
                        model = Attr;
                        var string = json[Attr].value;
                        var color = json[Attr].quality;
                        createStringOutput(id, string, color);

                    /* Here is checked the data format and if it is "SPECTRUM", 
                    cause if is it the case, we need to do a plot with the 
                    data.*/
                    
                    }else if(json[Attr].data_format == "SPECTRUM"){         

                        if(json[Attr].data_type == "DevString"){

                          var value = json[Attr].value; 
                          model = json[Attr].model;
                          createArrayOutput(id, value);

                        }else{

                          //var button = document.createElement("button");
                          //var text = document.createTextNode("View Plot");
                          
                          //value = json[Attr].value; 
                          //button.className = "btn btn-primary";
                          //button.right = "500px";
                          //button.style.align="center"; 


                          //button.onclick = function(){openPlot(id, value);};
                          //button.id = "View_plot";
                          //button.appendChild(text);
                          //table_forModalid.appendChild(button);
                          /*For activate the plots inside of the spectrum, just 
                          uncommnet this line*/
                          //Plot(model, value);
                        }
                    }
                }

            } else if (Attr.length>0) {
                var pre = document.createElement("pre");
                pre.innerHTML = Attr;
                pre.setAttribute("style","border: 0; margin: 10px;");
                document.getElementById(title_name).appendChild(pre);
            }
}


function openPlot(model, value){ 

    Plot(model, value);

    var button = document.createElement("button");
    var text = document.createTextNode("Close Plot");
    
    button.className = "btn btn-primary";
    button.onclick = function(){closePlot(model, value);}; 
    button.id = "Close_plot";
    button.appendChild(text);
    button.top = "400px";
    document.getElementById(model).appendChild(button);
    

}

function closePlot(model, value){

    var button = document.createElement("button");
    var text = document.createTextNode("View Plot");

    //$("#"+model).empty();
    button.className = "btn btn-primary";
    button.onclick = function(){openPlot(model, value);}; 
    button.id = "View_plot";
    button.appendChild(text);
    document.getElementById(model).appendChild(button);


}

/* Make the output of the beamlines, change the colors and the values */
function createStringOutput(model, string, color){


            var modelo = cleanString(model); 
            $("#"+modelo).text(string);

            var state = "alert alert-warning";
            
            if (color == "ATTR_VALID"){                    
                    state = "alert alert-success";
            }else if (color == "ATTR_WARNING"){
                    state = "alert alert-danger";
            }else if(color == "ATTR_ALARM"){
                    statee = "alert alert-warning";
            }else if(color == "ATTR_MOVING"){
                    state = "alert alert-info";
            }else if(color == "ATTR_NOT_FOUND"){
                    state = "alert alert-secondary"
            }

            document.getElementById(modelo).className = state
}

/*The same as the StringOutput but this is do it for the arrays */

function createArrayOutput(model, value){

        var model_in_html = cleanString(model);  
        if( $("#"+model_in_html).childElementCount != 0){

            var myNode = document.getElementById(model_in_html);
            var fc = myNode.firstChild;

            while( fc ) {
                myNode.removeChild( fc );
                fc = myNode.firstChild;
            }
        
        }
            for (var i=0; i<value.length; i++) { 

                var list = document.createElement("li");
                var valor = document.createTextNode(value[i]);
            
                list.className = "list-style";
                list.appendChild(valor);

                $("#"+model_in_html).append(list);
            }
    $("#"+model_in_html).removeAttr("style");

}



// Javascript function for refresh
function updateValues(jsondata){
        var data = jsondata.data
        for (var Attr in data){
            if(typeof data[Attr] !== "undefined" || data[Attr] === null){
                  var model;
                  if ( (data[Attr]).data_format == "SCALAR" ){
                      model = cleanString(data[Attr].section) +'_'+ Attr;
                      model = model.replace(/\ /g,"");

                      var string = data[Attr].value;
                      var color = data[Attr].quality;
                      createStringOutput(model, string, color);

                  }else if ( data[Attr].data_format == "SPECTRUM" ){
                      model = data[Attr].full_name;
                      model = cleanString(data[Attr].section) +'_'+ Attr;
                      model = model.replace(/\ /g,"");
                      var value = data[Attr].value;
                      updatePlot(model, value);

                  }
            }
           
        }
        var status =  document.getElementById(jsondata.section + "_state");   
        status.innerHTML = "Updated at " + jsondata.updatetime;
}


// Function of plot creation
function Plot(classID, model){
    // Plot options configuration


	var plotData = structure_config.data[model].value;
        var config = {
            type: 'line',

            
            data: {

                labels: [''],

                datasets: [ {

                    fill: false,
                    backgroundColor: window.chartColors.blue,
                    borderColor: window.chartColors.blue,
		    borderWidth: 1,
		    pointBorderWidth:0.1,
                    data: [],
                }]
            },
            options: {
                            vAxis: {minValue: 0},


		legend: {
		    display: false,
		    labels: {
			        fontSize: 0
			    }
		},
                responsive: true,
                title:{
                    display: false,
                    text:model,
                },
                tooltips: {
                    mode: 'index',
                    intersect: false,
                },
                hover: {
                    mode: 'nearest',
                    intersect: true
                },
                scales: {
                    xAxes: [{
                        display: true,
                        scaleLabel: {
                            display: true,
                            //labelString: 'Month'
                        },
		        ticks: {
			//autoSkip:true,
			maxTicksLimit:1
			}
                    }],
                    yAxes: [{
                        display: true,
                        scaleLabel: {
                            display: true,
                            //labelString: 'Value'
                        }
                    }]
                }
            }

}

	var canv = document.createElement('canvas');
	canv.id = classID+'_canvas';
		
	var elem = document.getElementById(classID)
	elem.appendChild(canv);

//	var ctx	= 	
//.getContext("2d");
        chart = new Chart(canv.getContext("2d"), config);
	myCharts[chart.chart.canvas.id] = chart;



    }


/*Refresh the plots, this function only works when we put the plot directly on the data label of the form*/
function updatePlot(id, data) {
    //$("#"+id+'_canvas').data;
    id = cleanString(id);  // Model of the beamline attribute to add
    var chart = myCharts[id+'_canvas'];
    var nums = [];
    for (var i = 0; i <= data.length; i++) {
	nums.push(i);
}
    chart.data.labels = nums;
    chart.data.datasets[0].data = data;
    chart.update();
    }
    /*id = cleanString(id);  // Model of the beamline attribute to add


    //pl = plotsSaved[id][0];

    $("#"+id).jqplot([data], plot_options);
    $("#"+id).data('jqplot');
    //$("#"+id).data('jqplot').series[0].data = [data];    
    //$("#"+id).data('jqplot').replot();
    $("#"+id).data('jqplot').redraw();
    //pl = $.jqplot (id, [data], plot_options);
    //plotsSaved[id][0] = pl;



}*/


/* Add Values to Modal on open it */

function getOutput(sectionName) {

    document.getElementById("Delete").removeAttribute("disabled");

    var container_txtArea = document.getElementById('attrs_label_modal');
    var container_description = document.getElementById('description_label_modal');
    var container_modalTitle = document.getElementById('title_label_modal');
    var container_hiddenModalTitle = document.getElementById
    ('hidden_title_label_modal');
    container_hiddenModalTitle.value = sectionName;
    container_modalTitle.value = sectionName;
    container_description.value = structure_config.config[sectionName].Description;
    var aux = structure_config.config[sectionName].Data;
    container_txtArea.value = "";
    for (var i = 0; i < aux.length; i++) {
        var str = aux[i]
        str = str.trim().split(/\s*,\s*/)
        container_txtArea.value += str + "\n";

    }
}


function expand(nameid){

    $("#"+nameid).click();
    return true;

}


