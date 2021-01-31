from data import info, scoringServer, dbInfo, getDivision, listens, divisions
from getpass import getpass
from os import path
import socket, pymongo, threading, datetime

def dbConnect(connInfo):
    if connInfo['user']:
        db = pymongo.MongoClient(
            connInfo['ip'],
            connInfo['port'],
            username=connInfo['user'],
            password=(
                connInfo['passwd'] or 
                getpass('Enter the password for your db: ')
                ),
            authsource=connInfo['authdb']
        ) [connInfo['name']]
    else:
        db = pymongo.MongoClient( 
            connInfo['ip'], 
            connInfo['port'],
        ) [connInfo['name']]
    return db
    
db = dbConnect(dbInfo)

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

    db.teams.insert_one({
        'uid' : '000000000000',
        'num' : '0000',
        'score' : -1
    })

    db.teams.create_index( 
        [('uid', pymongo.DESCENDING), ('competition', pymongo.DESCENDING)], 
        unique=True, name='one_team_uid_per_comp' )
    db.teams.create_index(
        [('num', pymongo.DESCENDING), ('competition', pymongo.DESCENDING)],
        unique=True, name='one_team_num_per_comp')
    db.teams.create_index( 
        [('competition', pymongo.DESCENDING), ('division', pymongo.DESCENDING)], 
        unique=True, name='one_div_per_comp' )
    
    with open("alreadyInit", "w") as checkFile:
        checkFile.writelines("completed")
    print("MongoDB initiaization completed")

listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

listener.bind( (scoringServer['ip'], scoringServer['port'] ) )

listener.listen( int( listens * 1.5 ) )
print('Listener activated')

def handleImage(connection):
    imageInfo = connection.recv(512).decode("utf-8")
    connection.close()

    imageInfo = imageInfo.split()
    imageInfo = {
        'teamID' : str(imageInfo[0]),
        'imageID' : str(imageInfo[1]),
        'os' : str(imageInfo[2]),
        'startTime' : 
            datetime.datetime.utcfromtimestamp( 
                float(imageInfo[3])
            ), # produces datetime.datetime object 
        'score' : int(imageInfo[4]),
        'vulnsFound' : int(imageInfo[5]),
        'timestamp' : datetime.datetime.utcnow()#.timestamp()
    }
    print(f"Received packet from image {imageInfo['imageID']}")

    # create a new client for each image connection
    db = dbConnect(dbinfo)

    # add team if not already registered
    db.teams.update_one(
        { 
            'uid' : imageInfo['teamID'], 
            'competition' : info['competitionName'],
            'startTime' : { '$exists' : False }
        }, { 
            '$set' : {
                'uid' : imageInfo['teamID'],
                'num' : imageInfo['teamID'][:4],
                'competition' : info['competitionName'],
                'division' : getDivision(imageInfo['teamID']),
                'startTime' : imageInfo['startTime'],
                'endTime' : imageInfo['timestamp'],
                'score' : 0
            }
        }
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
                    # and set the times
                    'startTime' : imageInfo['startTime'],
                    'endTime' : imageInfo['timestamp']
                } 
            }
        }
    )

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
                'images.$.vulns' : imageInfo['vulnsFound'] 
            },
            # add score record to list
            '$push' : {
                'images.$.scores' : {
                    'imageID' : imageInfo['imageID'],
                    'score' : imageInfo['score'],
                    'vulns' : imageInfo['vulnsFound'],
                    'time' : imageInfo['timestamp']
                }
            }
        }
    )

    # update composite score
    images = list( 
        db.teams.find({ 'uid' : imageInfo['teamID'] }, { 'images' : 1 }) 
        )[0]['images']
    db.teams.update_one(
        { 
            'uid' : imageInfo['teamID'],
            'competition' : info['competitionName']
        }, {
            '$set' : {
                'score' : sum([img['score'] for img in images])
            }
        }
    )

    conn.close()


# main loop
while True:
    imageSock, address = listener.accept()

    thread = threading.Thread(target=handleImage, args=(imageSock,))
    thread.start()