console.log("PhatBoi was here");
var cFrame = document.getElementById("scoreboard");
var canvas = cFrame.getContext("2d");
var widthOffset = 0.0;
var heightOffset = 0.0;
var width = cFrame.width - widthOffset;
var height = cFrame.height - heightOffset;

var graphX = 0.0;
var graphY = 0.0;

function update(){

    var xmlhttp = new XMLHttpRequest();
    var url = "Access-Control-Allow-Origin: http://18.191.223.30:8000/info/601615d8288ab5a37daf9745";//+window.location.pathname;
    var entry;
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            entry = JSON.parse(this.responseText);
        }
    };
    xmlhttp.open("GET", url);
    xmlhttp.send();
    
    var images = entry.images;
    canvas.clearRect(0, 0, width, height);
    canvas.lineWidth = 5;
    
    //Graph Section
    
    var maxScore = 0;
    for(var i = 0; i < images.length; i++){
        for(var j = 0; j < images[i].length; j++){
            if (images[i].scores[j].score > maxScore){
                maxScore = images[i].scores[j].score;
            }
        }
    }
    maxScore = Math.max(40, Math.ceil(maxScore / 10) * 10);
    canvas.strokeStyle = "#000000";
    for(var i = 0; i <= maxScore / 10; i++){
        canvas.beginPath();
        var drawHeight = height - 10 * i;
        canvas.moveTo(0 + graphX, drawHeight + graphY);
        canvas.lineTo(width + graphY, drawHeight + graphY);
        canvas.stroke();
    }
    for(var i = 0; i < images.length; i++){
        if (i % 3 == 0)
            canvas.strokeStyle = "#FF0000";
        else if (i % 3 == 1)
            canvas.strokeStyle = "#00FF00";
        else
            canvas.strokeStyle = "#0000FF";
        canvas.beginPath();
        canvas.moveTo(0 + graphX, 0 + graphY);
        for(var j = 0; j < images[i].length; j++){
            var mapHeight = map(images[i].scores[j].score, 0, maxScore, 0, height);
            mapHeight = height - mapHeight;
            canvas.lineTo(width * (j + 1.0) / images[i].scores.length + graphX, mapHeight + graphY);
        }
        canvas.stroke();
    }
    
    //Labeling Section
}

function map(v, a, b, c, d){
    return c + (v - a) * (d - c) / (b - a);
}
window.setInterval(update, 5 * 1000);
update();
