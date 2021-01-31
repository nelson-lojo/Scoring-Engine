info = {
    'organizerName' : 'cALi pAtrIot',
    'competitionName' : 'Practice Round',
    'divIDLen' : 2  # must be stricly < 8
                    # the shorter it is, 
                    #   the easier it is to 
                    #   impersonate another team
}

# this should be a publicly accessible interface
scoringServer = {
    'ip' : 'localhost',
    'port' : 69 #int(0)
}

# this should be a publicly accessible interface
web = {
    'root' : './',
    'ip' : '127.0.0.1',
    'port' : int(8080)
}

# this may (or may not) be a publicly accessible IP
# configure the way your organization desires 
#   if you don't know, then leave defaults
dbInfo = {
    'ip' : '3.140.134.99',
    'port' : 27017,
    'name' : 'notCP',
    'user' : 'nelly',
    'passwd' : '',
    'authdb' : 'admin'
}


divisions = {
    # 'Division # ID' should have a character between the division name and the component 
    #       with the last info['divIDLen'] characters as the ID of the division
    #           The ID of the division is parsed out of each team ID (as 
    #           implemented in getDivision())
    # 'image OS #' should have no spaces 
    #       this should also be the value in startingInfo['os'] on an image
    # ex:
    'XY' : (12, 'Windows10Home'),
    #'Division 1 ID' : 0,#(numOfTeams, 'image OS 1', 'image OS 2'),
    #'Division 2 ID' : 0,#(numOfTeams, 'image OS 1', 'image OS 2', 'image OS 3') 
}

def getDivision(teamID):
    for division in divisions:
        # this is the criteria for figuring out whether the 
        if division[ -info['divIDLen']: ] == teamID[ -info['divIDLen']: ]:
            return division[: -( 1 + info['divIDLen'] ) ]

listens = sum([ 
    divisions[division][0] * (len(divisions[division])-1) for division in divisions
    ])

