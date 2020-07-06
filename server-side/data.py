info = {
    'serverRoot' : '/scoringServer',
    'competitionName' : 'Practice Round',
    'divIDLen' : 3      # not (suppossed to be) referenced anywhere outside  
}

scoringServer = {
    'ip' : '',
    'port' : int(0)
}
web = {
    'ip' : '',
    'port' : int(0)
}
db = {
    'ip' : '',
    'port' : int(0),
    'name' : '',
    'user' : '',
    'passwd' : ''
}


divisions = {
    # 'Division # ID' should be a valid PostgreSQL table identifier 
    #       with the last info['divIDLen'] characters as the ID of the division
    #           The ID of the division can be parsed out of each team ID (as 
    #           implemented in getDivision())
    # 'image OS #' should be a valid PostgreSQL column identifier under 300 chars long
    #       this should also be the value in startingInfo['os'] on an image
    'Division 1 ID' : (numOfTeams, 'image OS 1', 'image OS 2'),
    'Division 2 ID' : (numOfTeams, 'image OS 1', 'image OS 2', 'image OS 3')
}

def getDivision(teamID):
    for division in divisions:
        # this is the criteria for figuring out whether the 
        if division[ -info['divIDLen']: ] == teamID[ -info['divIDLen']: ]:
            return division

listens = sum([ 
    divisions[division][0] * (len(divisions[division])-1) for division in divisions
    ])

