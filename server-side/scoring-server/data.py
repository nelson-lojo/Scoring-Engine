info = {
    'competitionName' : 'PracticeRound',
    'divIDLen' : 2  # must be stricly < 8
                    # the shorter it is, 
                    #   the easier it is to 
                    #   impersonate another team
}

# this should be a publicly accessible interface
scoringServer = {
    'ip' : '127.0.0.1',
    'port' : int(1069)
}

# this should be a publicly accessible interface
web = {
    'root' : '/scoreboard',
    'ip' : '',
    'port' : int(0)
}

# this may (or may not) be a publicly accessible IP
# configure the way your organization desires 
#   if you don't know, then leave defaults
dbInfo = {
    'ip' : '3.140.134.99',
    'port' : 27017,
    'name' : info['competitionName'],
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
    'Gold_ID' : (20, 'Windows10', 'Ubuntu16.04'),
    'Plat_XY' : (30, 'Windows10', 'Ubuntu16.04', 'WindowsServer2012R2')
}

def getDivision(teamID):
    for division in divisions:
        # this is the criteria for figuring out whether the 
        if division[ -info['divIDLen']: ] == teamID[ -info['divIDLen']: ]:
            return division[: -( 1 + info['divIDLen'] ) ]

listens = sum([ 
    divisions[division][0] * (len(divisions[division])-1) for division in divisions
    ])

