from data import info, dbInfo, divisions
import pymongo

db = pymongo.MongoClient( dbInfo['ip'], dbInfo['port'] ) [dbInfo['name']]

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