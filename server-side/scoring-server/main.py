import socket, pymongo, threading, datetime
from data import scoringServer, listens, dbInfo, getDivision


listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

listener.bind( (scoringServer['ip'], scoringServer['port'] ) )

listener.listen( int( listens * 1.5 ) )


db = pymongo.MongoClient( dbInfo['ip'], dbInfo['port'] ) [dbInfo['name']]

def handleImage(connection):
    imageInfo = connection.recv(512).decode("utf-8")
    connection.close()

    imageInfo = imageInfo.split()
    #* to be formatted properly
    imageInfo = {
        'teamID' : str(imageInfo[0]),
        'imageID' : str(imageInfo[1]),
        'os' : str(imageInfo[2]),
        'startTime' : imageInfo[3], #* timestamp
        'score' : int(imageInfo[4]),
        'vulnsFound' : int(imageInfo[5])
    }

    # add teams not already registered
    db.teams.update(
        { 'uid' : imageInfo['teamID'] },
        {
            'uid' : imageInfo['teamID'],
            'division' : getDivision(imageInfo['teamID'])
        }, upsert=True
    )

    # add images to list of images (if not already there)
    db.teams.update(
        { 'uid' : imageInfo['teamID'], 'images.name' : {'$ne' : imageInfo['os']} },
        { 
            '$push' : { 
                'images' : { 
                    'name' : imageInfo['os'],
                    'startTime' : imageInfo['startTime']
                } 
            }
        }
    )

    # add score record to list
    db.teams.update(
        { 'uid' : imageInfo['teamID'], 'images.name' : imageInfo['os'] },
        {
            '$push' : {
                'images.$.scores' : {
                    'imageID' : imageInfo['imageID'],
                    'score' : imageInfo['score'],
                    'vulns' : imageInfo['vulnsFound'],
                    'time' : datetime.datetime.utcnow()
                }
            }
        }
    )


# main loop
while True:
    imageSock, address = listener.accept()

    thread = threading.Thread(target=handleImage, args=(imageSock))
    thread.start()