// get input csv file name
var csvFileNameString = d3.select(".csvFileName").text();
csvFileNameString = csvFileNameString.replace(/ /g,'');
csvFileNameString = csvFileNameString.replace(/(\r\n|\n|\r)/gm,'');

//csvMetadata_list record item names
var csvMetadataString = d3.select(".csvMetadata").text();
// don't know why there are line breaks in the string
// use the following two lines to remove "tap" and line breaks
csvMetadataString = csvMetadataString.replace(/ /g,'');
csvMetadataString = csvMetadataString.replace(/(\r\n|\n|\r)/gm,'');
var csvMetadataList = csvMetadataString.split(',');



//d3.select(".aim_img").on("click",function(){ }
var myCanvas_width = 0;
var myCanvas_height = 0;
var myCanvas_x_offset = 0;
//var myCanvas_height = 0;
var position = 0;
window.onload = function() {

    document.getElementById("aim_img").style.visibility = "hidden";
    document.getElementById("loading_img").style.visibility = "hidden";

    var c = document.getElementById("myCanvas");
    var ctx=c.getContext("2d");
    var img=document.getElementById("aim_img");
    ctx.drawImage(img,0,0);

    position = getPosition(c);
    myCanvas_width = c.width;
    myCanvas_height = c.height;
    //myCanvas_height = c.height;
};

function getPosition(element) {
    var xPosition=0;
  
    while(element) {
        xPosition += (element.offsetLeft - element.scrollLeft + element.clientLeft);
        
        element = element.offsetParent;
    }
    //alert(xPosition);
    return xPosition;
}

// used to get html element position
// Based on: http://www.quirksmode.org/js/findpos.html
function getCumulativeOffset(obj) {
    var left, top;
    left = top = 0;
    if (obj.offsetParent) {
        do {
            left += obj.offsetLeft;
            top  += obj.offsetTop;
        } while (obj = obj.offsetParent);
    }
    return {
        x : left,
        y : top
    };
};

myCanvas_x_offset = getCumulativeOffset(document.getElementById("myCanvas")).x;

var coor1 = -1;
var coor2 = -1;
var coorBody1 = -1;
var coorBody2 = -1;


function mouseDown(event) 
{
    //alert("qqqq");
    var x = event.clientX;
    var y = event.clientY;
    coor1 = x;
    //alert(coor1);
}

function mouseUp(event) 
{
    var x = event.clientX;
    var y = event.clientY;
    coor2 = x;
    //alert(coor2);
    //alert(coor1+","+coor2);
    if (coor1 > coor2)
    {
        var temp = coor1;
        coor1 = coor2;
        coor2 = temp;
    }
}

function mouseDownBody(event) 
{
    //alert("qqqq");
    var x = event.clientX;
    var y = event.clientY;
    coorBody1 = x;
    //alert(coor1);
}

function mouseUpBody(event) 
{
    var x = event.clientX;
    var y = event.clientY;
    coorBody2 = x;
    if(coorBody1 > coorBody2)
    {
        var temp = coorBody1;
        coorBody1 = coorBody2;
        coorBody2 = temp;
    }

    var percent1 = 0;
    var percent2 = 0;

    if(coorBody1 != coor1 && coorBody2 == coor2)
    {
        coorBody1 = position;
        //alert(coorBody1+","+coorBody2);
    }
    else if(coorBody1 == coor1 && coorBody2 != coor2)
    {
        coorBody2 = position + myCanvas_width;
        ///alert(coorBody1+","+coorBody2);
    }
    else if(coorBody1 != coor1 && coorBody2 != coor2)
    {

        //alert('Outside');
    }
    else if(coorBody1 == coor1 && coorBody2 == coor2)
    {
        //alert(coorBody1+","+coorBody2);
    }
    var c = document.getElementById("myCanvas");
    var ctx=c.getContext("2d");
    // these are for rectangle
    // without beginPath() and closePath() the previous rectangle will be shown in the figure
    ctx.beginPath();
    ctx.rect(coorBody1-myCanvas_x_offset,0,coorBody2-coorBody1,myCanvas_width);
    ctx.stroke();
    ctx.closePath();

    percent1 = (100*(coorBody1-position)/myCanvas_width).toString();
    percent2 = (100*(coorBody2-position)/myCanvas_width).toString();
    //alert(percent1+","+percent2);
    
    coor1 = -1;
    coor2 = -1;
    coorBody1 = -1;
    coorBody2 = -1;
    
    // update vis part also based on checkbox
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
    //d3.select('.testP').text("/visualization/CSV_New/"+checkList+"/"+csvFileNameString+"/CSVNewUpdate/");
    // update div id = "lineChartdiv" after receive imgs
    var $image = $(".csv_results");
    var $downloadingImage = $("<img>");
    $downloadingImage.load(function(){
        $image.attr("src", $(this).attr("src"));    
    });
    //var img = document.getElementById("loading_img");
    //ctx.clearRect(0,0,myCanvas_width,myCanvas_height);
    //ctx.drawImage(img,0,0);
    //$downloadingImage.attr("src", "http://127.0.0.1:5000/visualization/CSV_New/temp_fig_4.png");
    //$downloadingImage.attr("src", "/visualization/CSV_New/CSV_New_Update/"+checkList);
    //d3.select('.testP').text("/visualization_results/zoom_in/"+checkList+"/"+percent1+"/"+percent2+"/"+csvFileNameString+'/');
    $downloadingImage.attr("src", "/visualization_results/zoom_in/"+checkList+"/"+percent1+"/"+percent2+"/"+csvFileNameString+'/');
    // must use this onload, or the program will not wait the backend finish process and use the previous result
    document.getElementById("aim_img").onload = function(){
        //ctx.clearRect(0,0,myCanvas_width,myCanvas_height);
        img=document.getElementById("aim_img");
        ctx.drawImage(img,0,0);
    }
}







