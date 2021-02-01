console.log("PhatBoi was here");
var parentDiv = document.getElementById("score_graph");
var cFrame = document.createElement('canvas');
cFrame.setAttribute("id", "scoreboard");
cFrame.setAttribute("width", parentDiv.clientWidth * 0.99);
cFrame.setAttribute("height", parentDiv.clientHeight);
cFrame.style.border = "none";
parentDiv.appendChild(cFrame);
var canvas = cFrame.getContext("2d");
var widthOffset = 40.0;
var heightOffset = 20.0 + 120;
var canvasWidth = cFrame.width;
var canvasHeight = cFrame.height;
alert(canvasWidth+" "+canvasHeight);
var width = canvasWidth - widthOffset;
var height = canvasHeight - heightOffset;

var graphX = 40.0;
var graphY = 20.0;

function update(){

    var xmlhttp = new XMLHttpRequest();
    var url = "/info/"+window.location.pathname.split('/')[2];
    var entry;
    xmlhttp.onload = function() {
        if (this.status == 200) {
            entry = JSON.parse(this.responseText);
            var images = entry.images;
            canvas.clearRect(0, 0, canvasWidth, canvasHeight);
            canvas.lineWidth = 1;
            
            var startTime = new Date(entry.startTime).getTime();
            var endTime = new Date(entry.endTime).getTime();
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
                canvas.lineTo(width + graphX, drawHeight + graphY);
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
                    var scoreTime = new Date(entry.images[i].scores[j].time).getTime();
                    var mapWidth = map(scoreTime, startTime, endTime, 0, width);
                    canvas.lineTo(mapWidth + graphX, mapHeight + graphY);
                }
                canvas.stroke();
            }
            
            //Labeling Section
            canvas.font = "15px Arial";
            canvas.textAlign = 'right';
            for(var i = 0; i <= maxScore / 10; i++){
                canvas.fillText("" + i * 10, graphX,  height - (10 * height / maxScore) * i + graphY - 1);
            }
            var labelAmount = 10;
            for(var i = 1; i <= labelAmount; i++){
                canvas.save();
                var dateTime = new Date(map(i, 0, labelAmount, startTime, endTime));
                var timeString = dateTime.toLocaleString();
                canvas.translate(width * i / labelAmount + graphX, height + graphY);
                canvas.textAlign = 'center';
                canvas.fillText("|", 0, 0);
                canvas.textAlign = 'right';
                canvas.rotate(-Math.PI/6);
                canvas.fillText(timeString, 0, 0);
                canvas.restore();
            }
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
