// timer
var start_time = Date.now();

//this js now only support the first element of the csv file to be the x axis
//and the first element should be date

//csvMetadata_list record item names
var csvMetadataString = d3.select(".csvMetadata").text();
// don't know why there are line breaks in the string
// use the following two lines to remove "tap" and line breaks
csvMetadataString = csvMetadataString.replace(/ /g,'');
csvMetadataString = csvMetadataString.replace(/(\r\n|\n|\r)/gm,'');
var csvMetadataList = csvMetadataString.split(',');

// get input csv file name
var imgString = d3.select(".imgName").text();
imgString = imgString.replace(/ /g,'');
imgString = imgString.replace(/			/g,'');
imgString = imgString.replace(/		/g,'');
imgString = imgString.replace(/(\r\n|\n|\r)/gm,'');

// get input csv file name
var csvFileNameString = d3.select(".csvFileName").text();
csvFileNameString = csvFileNameString.replace(/ /g,'');
csvFileNameString = csvFileNameString.replace(/			/g,'');
csvFileNameString = csvFileNameString.replace(/		/g,'');
csvFileNameString = csvFileNameString.replace(/(\r\n|\n|\r)/gm,'');


window.onload = function() {

    document.getElementById("aim_img").style.visibility = "hidden";

    var c = document.getElementById("myCanvas");
    var ctx=c.getContext("2d");
    var img=document.getElementById("aim_img");
    ctx.drawImage(img,0,0);
};


function change(checkBox) {
	lenList = csvMetadataList.length;
	checkList = '';
	// i starts from 2 not 0 or 1, this is because we skip the first column date
	// the loop.index is start with 1 not 0
	for(i=2 ; i<=lenList ; i++)
	{
		// if checked then 1, if not then 0
		if(d3.select('.checkBox'+i.toString()).property('checked'))
			checkList = checkList + '1';
		else
			checkList = checkList + '0';
	}
	// send a get request to the server side
	//d3.select('.testP').text("/CSV_New/"+checkList+"/"+imgString+"/CSVNewUpdate/");
	//d3.select('.testP').text("/CSV_New/"+checkList+"/"+imgString+"/CSVNewUpdate/");
	// update div id = "lineChartdiv" after receive imgs
	var $image = $(".csv_results");
	var $downloadingImage = $("<img>");
	$downloadingImage.load(function(){
 		$image.attr("src", $(this).attr("src"));	
	});
	//$downloadingImage.attr("src", "http://127.0.0.1:5000/visualization/CSV_New/temp_fig_4.png");
	//$downloadingImage.attr("src", "/visualization/CSV_New/CSV_New_Update/"+checkList);
	$downloadingImage.attr("src", "/CSV_New/"+checkList+"/"+imgString+"/CSVNewUpdate/");
	// must use this onload, or the program will not wait the backend finish process and use the previous result
	document.getElementById("aim_img").onload = function(){
	    var c = document.getElementById("myCanvas");
    	var ctx=c.getContext("2d");
    	var img=document.getElementById("aim_img");
   	 	ctx.drawImage(img,0,0);
	}

}



function screenShot()
{
	// select line chart div
    html2canvas(document.getElementById("lineChartdiv"), 
	{
		onrendered: function(canvas) {
			var img = canvas.toDataURL()
			window.open(img);
		}
    });	
}

function zoomOut()
{
	lenList = csvMetadataList.length;
	checkList = '';
	// i starts from 2 not 0 or 1, this is because we skip the first column date
	// the loop.index is start with 1 not 0
	for(i=2 ; i<=lenList ; i++)
	{
		// if checked then 1, if not then 0
		if(d3.select('.checkBox'+i.toString()).property('checked'))
			checkList = checkList + '1';
		else
			checkList = checkList + '0';
	}
	// send a get request to the server side
	d3.select('.testP').text("/CSV_New/"+checkList+"/"+csvFileNameString+"/zoomOut/");
	// update div id = "lineChartdiv" after receive imgs
	var $image = $(".csv_results");
	var $downloadingImage = $("<img>");
	$downloadingImage.load(function(){
 		$image.attr("src", $(this).attr("src"));	
	});
	//$downloadingImage.attr("src", "http://127.0.0.1:5000/visualization/CSV_New/temp_fig_4.png");
	//$downloadingImage.attr("src", "/visualization/CSV_New/CSV_New_Update/"+checkList);
	$downloadingImage.attr("src", "/CSV_New/"+checkList+"/"+csvFileNameString+"/"+imgString+"/zoomOut/");
	// must use this onload, or the program will not wait the backend finish process and use the previous result
	document.getElementById("aim_img").onload = function(){
	    var c = document.getElementById("myCanvas");
    	var ctx=c.getContext("2d");
    	var img=document.getElementById("aim_img");
   	 	ctx.drawImage(img,0,0);
	}
}
// timer
var end_time = Date.now();
//var time_used = end_time - start_time;
console.log("Time required to execute JavaScript code is : " + (end_time - start_time));