import pymongo
from data import dbInfo, divisions

db = pymongo.MongoClient( dbInfo['ip'], dbInfo['port'] ) [dbInfo['name']]

db.competitions.insert_one({ 
    'divisions' : [
        {
            'teams' : divisions[div][0],
            'images' : list( divisions[div][1:] )
        } 
        for div in divisions
    ]
})

teamCollection = db.teams

teamCollection.insert_one({
    'uid' : '0000-0000-0000',
    'num' : 0,
    'division' : 'plat'
})

teamCollection.create_index( [('num', pymongo.ASCENDING)], unique=True, name='unique_nums' )
teamCollection.create_index( [('uid', pymongo.DESCENDING)], unique=True, name='unique_uids' )
