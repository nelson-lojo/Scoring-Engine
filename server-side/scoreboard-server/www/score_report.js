window.addEventListener('load', (event) => {

    const newLocal = 750;
    var chart = new CanvasJS.Chart("score_graph", {
        
        animationEnabled: true,
        theme: "cyan2",
        title:{
            text: "Image scores",
            verticalAlign: "top",
            horizontalAlign: "left",
            fontFamily: "calibri",
            fontColor: "black"
        },
        axisX:{
            labelAngle: 145,
            labelMaxWidth: 200
        },
        axisY:{
        includeZero: false,
        maximum: 100
        },
        data: [{        
            type: "line",
            color: "orange",
            indexLabelFontSize: 12,
            dataPoints: [
                { y: 8, label: "12/07/19  09:00" },
                { y: 14, label: "12/07/19" },
                { y: 21, label: "12/07/19" },
                { y: 34, label: "12/07/19"},
                { y: 40, label: "12/07/19" },
                { y: 47, label: "12/07/19" },
                { y: 54, label: "12/07/19"},
                { y: 46, label: "12/07/19" },
                { y: 56, label: "12/07/19" },
                { y: 64, label: "12/07/19" },
                { y: 68, label: "12/07/19" },
                { y: 75, label: "12/07/19" },
                { y: 88, label: "12/07/19" },
                { y: 90, label: "12/07/19" },
                { y: 90, label: "12/07/19" }
            ]
        },
        {
            type: "line",
            color: "blue",
            indexLabelFontSize: 13,
            dataPoints: [
                { y: 5, label: "12/07/19  09:00" },
                { y: 10, label: "12/07/19" },
                { y: 16, label: "12/07/19" },
                { y: 24, label: "12/07/19"},
                { y: -30, label: "12/07/19" },
                { y: 40, label: "12/07/19" },
                { y: 48, label: "12/07/19"},
                { y: 56, label: "12/07/19" },
                { y: 62, label: "12/07/19" },
                { y: 64, label: "12/07/19" },
                { y: 70, label: "12/07/19" },
                { y: 72, label: "12/07/19" },
                { y: 76, label: "12/07/19" },
                { y: 82, label: "12/07/19" },
                { y: 84, label: "12/07/19" }
            ]
        }
    ]
    });
    chart.render(); 
    //{ y: 84 , indexLabel: "\u2193 lowest",markerColor: "DarkSlateGrey", markerType: "cross" }, lowest score
    //{ y: 34, indexLabel: "\u2191 highest",markerColor: "red", markerType: "triangle" }, highest score


    gentime = document.getElementById("gentime")
    if (gentime) {
        gentime.innerHTML = (new Date()).toISOString().replace('T', ' ').replace('Z', ' UTC');
    }
});