from data import info, scoringServer, dbInfo, getDivision, listens
import socket, pymongo, threading, datetime


listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

listener.bind( (scoringServer['ip'], scoringServer['port'] ) )

listener.listen( int( listens * 1.5 ) )

def handleImage(connection):
    imageInfo = connection.recv(512).decode("utf-8")
    connection.close()

    imageInfo = imageInfo.split()
    imageInfo = {
        'teamID' : str(imageInfo[0]),
        'imageID' : str(imageInfo[1]),
        'os' : str(imageInfo[2]),
        'startTime' : datetime.datetime.strptime( 
            str(imageInfo[3]) + str(imageInfo[4]) , 
            '%Y-%m-%d %H:%M:%S.%f' ), # produces datetime.datetime object 
        'score' : int(imageInfo[5]),
        'vulnsFound' : int(imageInfo[6]),
        'timestamp' : datetime.datetime.utcnow()
    }

    # create a new client for each image connection
    conn = pymongo.MongoClient( dbInfo['ip'], dbInfo['port'] )
    db = conn[dbInfo['name']]

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

    thread = threading.Thread(target=handleImage, args=(imageSock))
    thread.start()