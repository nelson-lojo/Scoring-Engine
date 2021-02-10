var fetchedTeams = 0;
var FETCH_INCREMENT = 15; // temporarily lowered for testing, will be between 100 and 200
var competition = null;
var division = null;

// send them to a team page #*

// data for when a value for competition is entered 
//     to update divisions dropdown
var organization = {
    "Something went wrong. Refresh your browser." : ["Something went wrong. Refresh your browser."]
};

// grab the current competition info
var compFetch = new XMLHttpRequest();
compFetch.open('GET', window.location.href + "/comps");
compFetch.onload = () => {
    organization = JSON.parse(compFetch.responseText);
};
compFetch.send(null);

window.addEventListener('load', (event) => {
    // toggle showing search for competitions 
    var compDropdown = document.getElementById("compDropdown");
    var compButton = document.getElementById("compButton");
    if (compDropdown && compButton) {
        compButton.addEventListener('click', (event) => {
            if (compDropdown.style.display === 'none') {
                compDropdown.style.display = "block";
                compDropdown.getElementsByTagName('input')[0].focus();
            } else {
                compDropdown.style.display = "none";
            }
        });
        compDropdown.style.display = 'none';
    }

    // toggle showing search for divisions 
    var divDropdown = document.getElementById("divDropdown");
    var divButton = document.getElementById("divButton");
    if (divDropdown && divButton) {
        divButton.addEventListener('click', (event) => {
            if (divDropdown.style.display === 'none') {
                divDropdown.style.display = 'block';
                divDropdown.getElementsByTagName('input')[0].focus();
            } else {
                divDropdown.style.display = 'none';
            }
        });
        divDropdown.style.display = 'none';
    }

    // make a tbody to add teams to
    var board = document.getElementsByTagName('table')[0];
    var list = document.createElement('TBODY');
    board.appendChild(list)
    
    // load `increment` teams to the list when the page loads #*
    refreshTeams(FETCH_INCREMENT);


    if (compDropdown) {
        compDropdown.addEventListener('input', (event) => {
            var input = compDropdown.getElementsByTagName('input')[0].value;
            if (input in organization) {
                // update the choices in divisions search when competitions search has a valid choice
                var list = organization[input];
                var cont = '';
                // build list of divisions in entered competition
                for (i = 0; i < list.length; i++) {
                    cont += '<option value="' + list[i] + '">\n'
                }
                divDropdown.getElementsByTagName('datalist')[0].innerHTML = cont;
                divDropdown.getElementsByTagName('input')[0].placeholder = "Search";

                // refresh list of teams upon entry of a valid competition
                refreshTeams(FETCH_INCREMENT);
            } else {
                if (divDropdown) {
                    divDropdown.getElementsByTagName('input')[0].placeholder = "Choose a valid Competition";
                    divDropdown.getElementsByTagName('datalist')[0].innerHTML = '';
                }
            }
        });
        if (divDropdown) {
            divDropdown.addEventListener('input', (event) => {
                // refresh list of teams upon entry of a valid combination of competition and division
                var comp = compDropdown.getElementsByTagName('input')[0].value;
                if ( (comp in organization) && (divDropdown.getElementsByTagName('input'[0]) in organization[comp]) ) {
                    refreshTeams(FETCH_INCREMENT);
                }
            });
        }
    }
});

// load more teams when they scroll to the bottom
window.addEventListener('scroll', (event) => {
    var scoreboard = document.getElementsByTagName('table')[0];
    if (scoreboard) {
        // check if they've reached the bottom and load more teams
        if ( (window.scrollY + window.innerHeight) >= document.body.offsetHeight ) {
            loadTeams(FETCH_INCREMENT);
        }
    }
});

function loadTeams(amount) {
    var fetch = new XMLHttpRequest();
    /*var uri = window.location.href + '/teams?';
    if (competition == null) {
        uri += '&competition=' + competition;
    }
    if (division == null) {
        uri += '&division=' + division;
    }
    fetch.open('POST', uri, true);
    */
    if (competition == null && division == null) {
        fetch.open('POST', window.location.href + '/teams', true);
    } else if (competition == null) {
        fetch.open('POST', window.location.href + '/teams?division=' + division, true);
    } else if (division == null) {
        fetch.open('POST', window.location.href + '/teams?competition=' + competition, true);
    } else {
        fetch.open('POST', window.location.href + '/teams?competition=' + competition + '&division=' + division, true); 
    }
    fetch.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    fetch.onload = (e) => {
        if(fetch.status == 200) {
            content = JSON.parse(fetch.responseText);
            table = document.getElementsByTagName('tbody')[0];
            // build table with teams
            for (team of content) {
                // calculate playtime for each team
                team.startTime = new Date( Date.parse(team.startTime) );
                if (!team.hasOwnProperty('endTime')) {
                    team.endTime = new Date();
                } else {
                    team.endTime = new Date( Date.parse(team.endTime) );
                }
                playtime = team.endTime.getTime() - team.startTime.getTime();

                // create a team's row
                var row = document.createElement("TR");
                row.setAttribute("onClick", "location.href='/team/"+team._id+"'");
                /*row.addEventListener('click', (event) => {
                    window.location="team/" + teamID;
                }) */
                uid = document.createElement("TD");
                uid.innerHTML = team.num;

                comp = document.createElement("TD");
                comp.innerHTML = team.competition;

                div = document.createElement("TD");
                div.innerHTML = team.division;

                playtyme = document.createElement("TD");
                minute = Math.floor(playtime / (1000 * 60) % 60);
                if(minute < 10){
                    minute = "0" + minute;
                }
                playtyme.innerHTML =  Math.floor(playtime / (1000 * 3600)) + ':' + minute;
                
                score = document.createElement("TD");
                score.innerHTML = team.score;
                
                warn = document.createElement("TD");
                var warnMsg = "";
                if(team.warn.multipleInstance){
                    warnMsg += "M";
                }
                if(team.warn.timeExceeded){
                    warnMsg += "T";
                }
                warn.innerHTML = warnMsg;
                
                row.appendChild(uid);
                row.appendChild(comp);
                row.appendChild(div);
                row.appendChild(playtyme);
                row.appendChild(score);
                row.appendChild(warn);
                
                console.log(["Loaded team:", team]);
                table.appendChild(row)
            }
        }
    };

    fetch.send("loaded=" + fetchedTeams + "&increment=" + amount);
    fetchedTeams += amount;
}

// reset the table of teams and load a new set of `initCount` teams
function refreshTeams(initCount) {
    var scoreboard = document.getElementsByTagName('tbody')[0];
    scoreboard.innerHTML = '';
    fetchedTeams = 0;
    loadTeams(initCount);
}
