from flask import Flask, render_template
from data import info, web, dbInfo
import pymongo, json
from bson.objectid import ObjectId

app = Flask(__name__)
db = pymongo.MongoClient(dbInfo['ip'], dbInfo['port'])[dbInfo['name']]


@app.route('/')
def serveScoreboard():
    comps = []
    divs = []
    return render_template('scoreboard.html', competitions=comps, divisions=divs)
#    return static_file("scoreboard.html", root=f"{web['root']}/www") 

@app.route('/comps')
def serveCompetitionsAndDivisions():
    return json.dumps( list( db.competitions.find() ) )


@app.route('/teams', methods=['POST'])
def postTeams(loaded=0):
    comp = request.query.competition
    div = request.query.division
    loaded = request.forms.get('loaded')
    increment = request.forms.get('increment')

    return json.dumps( 
        list(
            db.teams.find(
                {
                    'division' : div,
                    'competition' : comp
                }, {
                    # '_id' : 0,
                    'num' : 1,
                    'competition' : 1,
                    'division' : 1,
                    'startTime' : 1,
                    'endTime' : 1,
                    'score' : 1,
                    'warnings' : 1 #* include warnings
                }
            )
            .sort({"score" : -1})
            .skip(loaded)
            .limit(increment)
        )
    )

@app.route('/team/<teamid>') #*
def serveTeamSummary(teamid):
    team = db.teams.find( { '_id' : ObjectId(teamid) } )[0]
    return render_template('score_report.html', id=str(team._id)[-4:], division=team.division, images=team.images, play_time=(team.endTime - team.startTime), total_score=team.score, warnings= )

if __name__ == "__main__":
    app.run(host=web['ip'], port=web['port'], reloader=True) 