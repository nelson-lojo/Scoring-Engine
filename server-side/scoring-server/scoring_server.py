from data import info, scoringServer, dbInfo, getDivision, listens, divisions
from getpass import getpass
from json import loads
from os import path
import socket, pymongo, threading, datetime

def log(category='MISC', message=''):
    with open("scoring_server.log", "a+") as logFile:
        logFile.writelines(f"[{category}]: {message}")

def dbConnect(connInfo):
    if connInfo['user']:
        conn = pymongo.MongoClient(
            connInfo['ip'],
            connInfo['port'],
            username=connInfo['user'],
            password=(
                connInfo['passwd'] or 
                getpass('Enter the password for your db: ')
                ),
            authsource=connInfo['authdb']
        )
    else:
        conn = pymongo.MongoClient( 
            connInfo['ip'], 
            connInfo['port'],
        )
    return conn

def handleImage(connection, connInfo):
    msg = connection.recv(1024).decode("utf-8")
    connection.close()

    imageInfo = loads(msg)
    imageInfo.update({
        'division' : getDivision(str(imageInfo[0])),
        'startTime' : 
            datetime.datetime.fromtimestamp( 
                imageInfo['startTime']
            ), # produces datetime.datetime object 
        'score' : int(imageInfo['score']),
        'vulnsFound' : int(imageInfo['vulnsFound']),
        'maxVulns' : int(imageInfo['maxVulns']),
        'foundPens' : int(imageInfo['foundPens']),
        'timestamp' : datetime.datetime.utcnow()#.timestamp()
    })
    print(f"Received packet from image {imageInfo['imageID']}")
    # print(f"Recieved \t {msg}")
    
    divisionID = (filter(lambda ID: imageInfo['division'] in ID, divisions.items()))[0]
    
    if imageInfo['startTime'] - (time:= datetime.datetime.now()) > info['timingTolerance']:
        print(f"Start time for image {imageInfo['imageID']} was spoofed to be {imageInfo['startTime']} at {datetime.datetime.now()}, exceeding the tolerance of {info['timingTolerance']}")
        return 
    elif imageInfo['os'] not in divisions[divisionID]:
        print(f"Team {imageInfo['teamID']} has an invalid image running {imageInfo['os']}")
        return

    # create a new client for each image connection
    conn = dbConnect(dbInfo)
    db = conn[dbInfo['name']]

    # add team if not already registered
    db.teams.update_one(
        { 
            'uid' : imageInfo['teamID'], 
            'competition' : info['competitionName']
        }, { 
            '$set' : {
                'uid' : imageInfo['teamID'],
                'competition' : info['competitionName'],
                'num' : imageInfo['teamID'][:4],
                'division' : imageInfo['division'],
                'endTime' : imageInfo['timestamp'],
                'score' : 0,
                'warn' : {
                    'multipleInstance' : False,
                    'timeExceeded' : False,
                }
            }
        }, 
        upsert=True
    )

    # update team start and end time
    db.teams.update_one(
        {
            'uid' : imageInfo['teamID'],  
            'competition' : info['competitionName'],
        },
        {
            # set earliest start time
            '$min' : { 'startTime' : imageInfo['startTime'] },
            # set latest end time
            '$max' : { 'endTime' : imageInfo['timestamp'] }
        }
    )

    # add image if not already there
    db.teams.update_one(
        { 
            'uid' : imageInfo['teamID'],
            'competition' : info['competitionName'],
            'images.name' : { '$ne' : imageInfo['os'] } 
        }, { 
            # add images to list of images (if not already there)
            '$push' : { 
                'images' : { 
                    'name' : imageInfo['os'],
                    # set the score for the image 
                    'score' : imageInfo['score'],
                    'vulns' : imageInfo['vulnsFound'],
                    'pens' : imageInfo['foundPens'],
                    'maxVulns' : imageInfo['maxVulns'],
                    # and set the times
                    'startTime' : imageInfo['startTime'],
                    'endTime' : imageInfo['timestamp']
                } 
            }
        }
    )

    # get the last two packets recieved
    im_scores = list(
        db.teams.aggregate([
            {
                '$match' : {
                        'uid': imageInfo['teamID'], 
                        'competition': info['competitionName']
                }
            },
            { '$unwind': '$images' },
            { '$match': {'images.name': imageInfo['os'] } },
            { '$project' : {
                    'start' : '$images.startTime',
                    'lastLast' : { '$arrayElemAt' : [ "$images.scores", -2 ] },
                    'last' : { '$arrayElemAt' : [ "$images.scores", -1 ] }
                }
            }
        ])
    )
    multipleInstance = False
    timeExceeded = False

    if len(im_scores):
        query = im_scores[0]
        # print(f"returned query: {query}")

        exists = bool(
            query.get('last', None) and query.get('lastLast', None)
        )

        multipleInstance = exists and ( 
            query['last']['imageID'] != imageInfo['imageID']
                and 
            query['lastLast']['imageID'] == imageInfo['imageID'] 
        )
        timeExceeded = (imageInfo['timestamp'] - query['start']) > info['maxTime']

    warnDict = {
        'multipleInstance' : multipleInstance,
        'timeExceeded' : timeExceeded
    }
    # update image info
    db.teams.update_one(
        { 
            'uid' : imageInfo['teamID'], 
            'competition' : info['competitionName'],
            'images.name' : imageInfo['os']
        }, {
            # update image times
            '$min' : { 'images.$.startTime' : imageInfo['startTime'] },
            '$max' : { 'images.$.endTime' : imageInfo['timestamp'] },
            # set image score
            '$set' : { 
                'images.$.score' : imageInfo['score'],
                'images.$.vulns' : imageInfo['vulnsFound'],
                'images.$.warn' : warnDict
            },
            # add score record to list
            '$push' : {
                'images.$.scores' : {
                    'imageID' : imageInfo['imageID'],
                    'score' : imageInfo['score'],
                    'vulns' : imageInfo['vulnsFound'],
                    'time' : imageInfo['timestamp'],
                    'warn' : warnDict
                }
            }
        }
    )

    # update composite score
    team = list(
        db.teams.find({ 'uid' : imageInfo['teamID'] }, { 'images' : 1 }) 
        )
    if team:
        images = team[0]['images']
        db.teams.update_one(
            { 
                'uid' : imageInfo['teamID'],
                'competition' : info['competitionName']
            }, {
                '$set' : {
                    'score' : sum([img['score'] for img in images]),
                    'warn' : warnDict
                }
            }
        )
    else:
        pass

    conn.close()

if __name__ == '__main__':
    dbInfo['passwd'] = getpass('Enter the password for your db: ')
    db = dbConnect(dbInfo)[dbInfo['name']]

    if not (path.exists("alreadyInit")):
        # there's nothing in the checkfile, so 
        # do init script    

        db.competitions.insert_one({ 
            'name' : info['competitionName'],
            'divisions' : [
                {
                    'name' : div[ : -( 1 + info['divIDLen'] ) ],
                    'teams' : divisions[div][0],
                    'images' : list( divisions[div][1:] )
                } 
                for div in divisions
            ]
        })

        db.teams.create_index( 
            [('uid', pymongo.DESCENDING), ('competition', pymongo.DESCENDING)], 
            unique=True, name='one_team_uid_per_comp' )
        db.teams.create_index(
            [('num', pymongo.DESCENDING), ('competition', pymongo.DESCENDING)],
            unique=True, name='one_team_num_per_comp')
        db.teams.create_index( 
            [('competition', pymongo.DESCENDING), ('division', pymongo.DESCENDING)], 
            unique=False, name='comp_and_div_lookup' )
        
        with open("alreadyInit", "w") as checkFile:
            checkFile.writelines("completed")
        print("MongoDB initiaization completed")

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind( (scoringServer['ip'], scoringServer['port'] ) )
    listener.listen( int( listens * 1.5 ) )
    print('Listener activated')

    # main loop
    while True:
        try:
            imageSock, address = listener.accept()

            thread = threading.Thread(target=handleImage, args=(imageSock, dbInfo,))
            thread.start()
        except:
            listener.close()
