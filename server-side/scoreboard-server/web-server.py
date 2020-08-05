from flask import Flask, render_template
from data import info, web, dbInfo
import pymongo, json

app = Flask(__name__)
db = pymongo.MongoClient(db['ip'], db['port'])[db['name']]


@app.route('/')
def scoreboard():
    comps = []
    divs = []
    return render_template('scoreboard.html', competitions=comps, divisions=divs)
#    return static_file("scoreboard.html", root=f"{web['root']}/www") 


@app.post('/teams')
def postTeams(loaded=0):
    comp = request.query.competition
    div = request.query.division
    loaded = request.forms.get('loaded')

    teams = list(
        db.teams.find(
            {
                'division' : div,
                'competition' : comp
            }, {
                'num' : 1,
                'competition' : 1,
                'division' : 1,
                'startTime' : 1,
                'endTime' : 1,
                'score' : 1
            }
        )
        .sort({"score" : -1})
        .skip(loaded)
        .limit(35)
    )

    return json.dumps(teams)


@app.route('/team/<teamid>') #*
def showTeam(teamid):
    db.teams.find( { '_id' : pymongo.ObjectID(teamid) } )

if __name__ == "__main__":
    app.run(host=web['ip'], port=web['ports'], reloader=True) 