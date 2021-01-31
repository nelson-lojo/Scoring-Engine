console.log("PhatBoi was here");
var cFrame = document.getElementById("scoreboard");
var canvas = cFrame.getContext("2d");
cFrame.style.border = "none";
var widthOffset = 40.0;
var heightOffset = 40.0;
var width = cFrame.width - widthOffset;
var height = cFrame.height - heightOffset;

var graphX = 20.0;
var graphY = 20.0;

function update(){

    var xmlhttp = new XMLHttpRequest();
    var url = "/info/601615d8288ab5a37daf9745";//+window.location.pathname;
    var entry;
    xmlhttp.onload = function() {
        if (this.status == 200) {
            entry = JSON.parse(this.responseText);
            var images = entry.images;
            canvas.clearRect(0, 0, width, height);
            canvas.lineWidth = 1;
            
            //Graph Section
            
            var maxScore = 0;
            for(var i = 0; i < images.length; i++){
                for(var j = 0; j < images[i].scores.length; j++){
                    if (images[i].scores[j].score > maxScore){
                        maxScore = images[i].scores[j].score;
                    }
                }
            }
            maxScore = Math.max(40, Math.ceil(maxScore / 10) * 10);
            canvas.strokeStyle = "#b5b5b5";
            for(var i = 0; i <= maxScore / 10; i++){
                canvas.beginPath();
                var drawHeight = height - (10 * height / maxScore) * i;
                canvas.moveTo(0 + graphX, drawHeight + graphY);
                canvas.lineTo(width + graphY, drawHeight + graphY);
                canvas.stroke();
            }
            canvas.lineWidth = 3;
            for(var i = 0; i < images.length; i++){
                if (i % 3 == 0)
                    canvas.strokeStyle = "#FF0000";
                else if (i % 3 == 1)
                    canvas.strokeStyle = "#00FF00";
                else
                    canvas.strokeStyle = "#0000FF";
                canvas.beginPath();
                canvas.moveTo(0 + graphX, height + graphY);
                for(var j = 0; j < images[i].scores.length; j++){
                    var mapHeight = map(images[i].scores[j].score, 0, maxScore, 0, height);
                    mapHeight = height - mapHeight;
                    canvas.lineTo(width * (j + 1.0) / images[i].scores.length + graphX, mapHeight + graphY);
                }
                canvas.stroke();
            }
            
            //Labeling Section
        }
    };
    xmlhttp.open("GET", url);
    xmlhttp.send();
    
}

function map(v, a, b, c, d){
    return c + (v - a) * (d - c) / (b - a);
}
window.setInterval(update, 10 * 1000);
update();
