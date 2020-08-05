var fetchedTeams = 0;
var fetchIncrement = 35;
var competition = null;
var division = null;

// when the page first loads, load 35 teams #*
// send them to a team page #*
// load teams when they scroll #*




// when a value for competition is entered, update divisions dropdown
var organization = {
    "comp 1" : ["div 1", "div 2"],
    "comp 2" : ["div 1", "div 2", "div 3"]
};

/*
    var compDrop = document.createElement("div")
    compDrop.id = "compDropdown";
    compDrop.className = "dropdown";

    var compSearchbox = document.createElement("input");
    compSearchbox.type = 'text';
    compSearchbox.placeholder = "Search";
    compSearchbox.size = 16;
    compSearchbox.list = "compSearch";
    compDrop.appendChild(compSearchbox);

    var compList = document.createElement("datalist");
    compList.id = "compSearch";
    for (i = 0; i < organization.length; i++) {
        var op = document.createElement('option');
        op.value = organization[i];
        compList.appendChild(op);
    }
    compDrop.appendChild(compList);

    document.getElementById("dropdowns").appendChild(compDrop); 
// */


window.addEventListener('load', (event) => {
    // toggle showing search for competitions 
    var compDroppy = document.getElementById("compDropdown");
    var compButton = document.getElementById("compButton");
    if (compDroppy && compButton) {
        compButton.addEventListener('click', (event) => {
            if (compDroppy.style.display === 'none') {
                compDroppy.style.display = "block";
                compDroppy.getElementsByTagName('input')[0].focus();
            } else {
                compDroppy.style.display = "none";
            }
        });
        compDroppy.style.display = 'none';
    }

    // toggle showing search for divisions 
    var divDroppy = document.getElementById("divDropdown");
    var divButton = document.getElementById("divButton");
    if (divDroppy && divButton) {
        divButton.addEventListener('click', (event) => {
            if (divDroppy.style.display === 'none') {
                divDroppy.style.display = 'block';
                divDroppy.getElementsByTagName('input')[0].focus();
            } else {
                divDroppy.style.display = 'none';
            }
        });
        divDroppy.style.display = 'none';
    }

    if (compDroppy) {
        compDroppy.addEventListener('input', (event) => {
            if (compDroppy.getElementsByTagName('input')[0].value in organization) {
                // update the choices in divisions search when competitions search has a valid choice
                var list = organization[compDroppy.getElementsByTagName('input')[0].value];
                var cont = ''
                for (i = 0; i < list.length; i++) {
                    cont += '<option value="' + list[i] + '">\n'
                }
                divDroppy.getElementsByTagName('datalist')[0].innerHTML = cont
                divDroppy.getElementsByTagName('input')[0].placeholder = "Search"

                // refresh list of teams
                document.getElementsByTagName('table')[0].innerHTML = '<thead>' 
                        + '<th>Team ID</th>' 
                        + '<th>Competition</th>' 
                        + '<th>Division</th>' 
                        + '<th>Play Time</th>' 
                        + '<th>Score</th>' 
                        + '<th>Warning(s)</th>' 
                        + '</thead>';

                // loadTeams
                // #*
            } else {
                if (divDroppy) {
                    divDroppy.getElementsByTagName('input')[0].placeholder = "Choose a valid Competition";
                    divDroppy.getElementsByTagName('datalist')[0].innerHTML = '';
                }
            }
        });
    }
});


// on the entrance of a competition value or division value
// document.getElementById("").addEventListener('input', (event) => {
//     // send another request: loadTeams(newComp/newDiv) #*
// });

// function loadTeams() {
//     var fetch = new XMLHttpRequest();
//     fetch.open('POST', window.location.href + '/teams?competition=' + competition + '&division='+ division); 
//     fetch.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
//     fetch.onload = function() {
//         if(this.status == 200) {
//             content = JSON.parse(fetch.responseText);
//             table = ''
//             playtime = team.endTime - team.startTime  // make sure this are date objects #* 
//             for (team of content) {
//                 table += '<tr>' +
//                     '<td>' + team.num + '</td>' +
//                     '<td>' + team.competition + '</td>' +
//                     '<td>' + team.division + '</td>' +
//                     '<td>' + playtime.getHours() + ':' + playtime.getMinutes() + '</td>' +
//                     '<td>' + team.score + '</td>' +
//                     '</tr>'
//             }
//             document.getElementsByTagName('table')[0].innerHTML += fetch.responseText
//         }
//     };

//     fetch.send("loaded=" + fetchedTeams);
//     fetchedTeams += fetchIncrement;
// }

