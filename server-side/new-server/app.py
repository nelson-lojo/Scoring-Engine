from datetime import datetime
import json
from data import info, server
from flask import Flask, redirect, url_for, render_template, send_from_directory, request
from models.competition import Competition
from models.team import Team
from models.image import Image
from models.report import Report

app = Flask(__name__)

@app.route('/')
def toScoreboard():
    return redirect(url_for('scoreboard'))

# default route
@app.route('/<resource>')
def serveResource(resource):
    return send_from_directory('www', resource)#f"www/{resource}")

@app.route('/scoreboard')
def scoreboard():
    raise NotImplementedError
    # expect this to call /teams with ajax
    return render_template('scoreboard.html', **data)

@app.route('/teams')
def indexTeams(comp):
    # use url params (...?comp=[]&div=[])
    # index teams filtered by competition / division
    raise NotImplementedError
    data = {
        'organization' : info['organizerName'],
        'competitions' : comps,
        'divisions'    : divs
    }
    return json.dumps()

@app.route('/team/<id>')
def readTeam(id):
    # expect this to call /team/<id>/json with ajax
    raise NotImplementedError

@app.route('/team/<id>/json')
def readTeamJSON(id):
    raise NotImplementedError
    return Team.where('uid', '=', id).first().serialize()

@app.route('/score', methods = ['POST'])
def score():
    # get the image data from the post body
    data = json.loads(request.json)

    report = Report(**data)

    if not (image := Image.where('uid', '=', report.imageID)):
        image = Image(data['os'], data['imageID'])
         
    image.score = report.score
    image.id = report.imageID
    image.reports.add(report)
    
    
    if not (team := Team.where('uid', '=', data['teamID']).first()):
        team = Team(data['teamID'], data['startTime'], report.timestamp)
    
    team.endTime = report.timestamp

    

    # team.score = data['score']
    
    # get object reps for
    #   competition + division
    #   team
    #   image
    #   report
    # create the team and image if they don't already exist
    # always make a new report
    # then add the report to the image


if __name__ == '__main__':
    app.run(host=server['ip'], port=server['port'])