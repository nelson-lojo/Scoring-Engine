from flask import Flask, render_template, send_from_directory, request
from datetime import date, datetime
from data import info, web, dbInfo
from bson.objectid import ObjectId
from getpass import getpass
import pymongo, json

app = Flask(__name__)

if dbInfo['user']:
    db = pymongo.MongoClient(
        dbInfo['ip'],
        dbInfo['port'],
        username=dbInfo['user'],
        password=(
            dbInfo['passwd'] or 
              getpass('Enter the password for your db: ')
            ),
        authsource=dbInfo['authdb']
    ) [dbInfo['name']]
else:
    db = pymongo.MongoClient( 
        dbInfo['ip'], 
        dbInfo['port'],
    )[dbInfo['name']]

# serve the scoreboard
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

# default route for non-html resources
@app.route('/<resource>')
def serveResource(resource):
    return send_from_directory('www', resource)#f"www/{resource}")



# get the competitions and their divisions as json
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

# get all the teams in a competition and division as json
@app.route('/teams', methods=['POST'])
def postTeams(loaded=0):
    comp = request.args.get('competition', None) or {'$regex': '.*'}
    div = request.args.get('division', None) or {'$regex': '.*'}
    loaded = request.form.get('loaded')
    # print(loaded, ':', type(loaded))
    increment = request.form.get('increment')

    return json.dumps( 
        list(
            db.teams.find(
                {
                    'division' : div,
                    'competition' : comp
                }, {
                    '_id' : 1,
                    'num' : 1,
                    'competition' : 1,
                    'division' : 1,
                    'startTime' : 1,
                    'endTime' : 1,
                    'score' : 1,
                    'warn' : 1 
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

# serve team score summary
@app.route('/team/<teamid>') #*
def serveTeamSummary(teamid):
    # return str(team)
    team = list(db.teams.find( { '_id' : ObjectId(teamid) } ))[0]
    # return str(team)
    team['endTime'] = team.get('endTime', datetime.now())
    # for i in range(len(team['images'])):
    #     image = team['images'][i]
    #     image['']
    # return f"eyy: {teamid}"
    # return str(team)
    # assert False
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

# get the score information as json
@app.route('/info/<teamid>')
def serveScoreInfo(teamid):
    return json.dumps( 
        list( db.teams.find( { '_id' : ObjectId(teamid) } ) )[0],
        default=(
            lambda obj: (
                obj.isoformat() if isinstance(obj, (datetime, date)) else (
                    str(obj) if isinstance(obj, ObjectId) else None
                )
            )
        )
    )


if __name__ == "__main__":
    app.run(host=web['ip'], port=web['port'], debug=True)#, reloader=True) 
