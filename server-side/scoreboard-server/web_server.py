from flask import Flask, render_template, send_from_directory, request
from data import info, web, dbInfo
from datetime import date, datetime
import pymongo, json
from bson.objectid import ObjectId

app = Flask(__name__)
db = pymongo.MongoClient(dbInfo['ip'], dbInfo['port'])[dbInfo['name']]


@app.route('/')
def serveScoreboard():
    comps, divs = [], {}
    query = list(db.competitions.find())
    for comp in query:
        comps.append(
            comp['name']
        )
        divs[comp['name']] = [ div['name'] for div in comp['divisions'] ]
    return render_template('scoreboard.html', Organization=info['organizerName'], competitions=comps, divisions=divs)
#    return static_file("scoreboard.html", root=f"{web['root']}/www") 

@app.route('/comps')
def serveCompetitionsAndDivisions():
    return json.dumps( 
        list( 
            db.competitions.find(
                {},
                {
                    '_id' : 0,
                    'name' : 1,
                    'divisions.name' : 1
                }
            ) 
        ) 
    )

@app.route('/<resource>')
def serveResource(resource):
    return send_from_directory('www', resource)#f"www/{resource}")

@app.route('/teams', methods=['POST'])
def postTeams(loaded=0):
    comp = request.args.get('competition') or {'$regex': '.*'}
    div = request.args.get('division') or {'$regex': '.*'}
    loaded = request.form.get('loaded')
    # print(loaded, ':', type(loaded))
    increment = request.form.get('increment')

    return json.dumps( 
        list(
            db.teams.find(
                {
                    'division' : {'$regex': '.*'}, #div,
                    'competition' : {'$regex': '.*'}#comp
                }, {
                    '_id' : 1,
                    'uid' : 1,
                    'competition' : 1,
                    'division' : 1,
                    'startTime' : 1,
                    'endTime' : 1,
                    'score' : 1,
                    'warnings' : 1 #* include warnings
                }
            )
            .sort([("score", pymongo.DESCENDING)])
            .skip(int(loaded))
            .limit(int(increment))
        ),
        default=(
            lambda obj: (
                obj.isoformat() if isinstance(obj, (datetime, date)) else (
                    str(obj) if isinstance(obj, ObjectId) else None
                )
            )
        )
    )

@app.route('/team/<teamid>') #*
def serveTeamSummary(teamid):
    team = list(db.teams.find( { '_id' : ObjectId(teamid) } ))[0]
    team['endTime'] = team.get('endTime', datetime.now())
    for i in range(len(team['images'])):
        image = team['images'][i]
        image['']


    return render_template(
        'score_report.html', 
        id=str(team['_id'])[-4:], 
        division=team['division'], 
        im_no=len(team['images']),
        images=team['images'], 
        play_time=(team['endTime'] - team['startTime']), 
        total_score=team['score'], 
        warnings='' 
    )

if __name__ == "__main__":
    app.run(host=web['ip'], port=web['port'], debug=True)#, reloader=True) 