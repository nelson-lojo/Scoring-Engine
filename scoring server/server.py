import socket, threading, datetime, psycopg2
from psycopg2 import SQL, Identifier

publicAccess = ('ip/dns', int('port'))
dbInfo = {
#    'location' : '',
    'name' : '',
    'user' : '',
    'pass' : ''
}
divisions = {
    # 'Division #' should be a valid PostgreSQL table identifier
    # 'image OS #' should be a valid PostgreSQL column identifier under 300 chars long
    #       this should also be the value in startingInfo['os'] on an image
    'Division 1' : (numOfTeams, 'image OS 1', 'image OS 2'),
    'Division 2' : (numOfTeams, 'image OS 1', 'image OS 2', 'image OS 3')
}
listens = 0

db = psycopg2.connect(f"dbname={dbInfo['name']} user={dbInfo['user']}")
initConsole = db.cursor()

for division in divisions:
    # add up how many connections to allow to the server from this division
    listens += divisions[division][0] * (len(divisions[division])-1)


    division_table = f"{division}"
    images_table = f"{division}_images"
    # make images_table for this division
    # CREATE TABLE images_table ( 
    #     image_id VARCHAR(129) PRIMARY KEY,
    #     system_type VARCHAR(300) NOT NULL,
    #     score INT NOT NULL,
    #     vulns_found INT NOT NULL,
    #     start_time TIMESTAMP NOT NULL
    # );
    initConsole.execute(
        SQL(
        """
            CREATE TABLE {table} (
                image_id VARCHAR(129) PRIMARY KEY,
                system_type VARCHAR(300) NOT NULL,
                score INT NOT NULL,
                vulns_found INT NOT NULL,
                start_time TIMESTAMP NOT NULL
            );
        """
        ).format(
            table=Identifier(images_table)
        )
    )

    # create the segment of the SQL command in the creation of the division table
    image_cols = ''
    for image in divisions[division][1:]:
        image_cols += "{column} VARCHAR(129) REFERENCES {foreign_table} (image_id), ".format(
            column=Identifier(f"{image}_id"),
            foreign_table=Identifier(images_table)
        )

    # make the table for this division 
    # CREATE TABLE division_table (
    #       team_id VARCHAR (12), 
    #       os1_id VARCHAR(129) REFERENCES images_table (image_id), 
    #       os2_id VARCHAR(129) REFERENCES images_table (image_id), 
    #       ..., 
    #       start_time
    # );
    initConsole.execute(
        SQL(
        """
            CREATE TABLE {table} ( 
                team_id VARCHAR(12) PRIMARY KEY,
                {image_id_columns}
                start_time TIMESTAMP NOT NULL
                );
        """).format(
            table=Identifier(division_table),
            image_id_columns=image_cols
        )
    )
initConsole.close()

mySock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mySock.bind(publicAccess)
mySock.listen( int(listens * 1.5) )  # 1.5 is a tolerance level

def getDivision(teamID):
    pass

def markAsDupImage(teamID, os):
    pass

def handleImage(sock):
    imageInfo = sock.recv(512).decode("utf-8")
    sock.close()

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
    division = getDivision(imageInfo['teamID'])

    dbConsole = db.cursor()

    # SELECT team_id FROM division_table WHERE team_id = given_team_id;
    dbConsole.execute(
        SQL(
            "SELECT team_id FROM {table} WHERE team_id=%s LIMIT 1;"
        ).format(
            table=Identifier(f"{division}")
        ),
        (imageInfo['teamID'])
    )
    if dbConsole.fetchone(): # the team is in the competition table AKA ^^^ returns a row
        # SELECT os_id FROM division_table WHERE team_id = given_team_id;
        dbConsole.execute(
            SQL(
                "SELECT {column} FROM {table} WHERE team_id=%s;"
            ).format(
                column=Identifier(f"{imageInfo['os']}_id"),
                table=Identifier(f"{division}")
            ),
            (imageInfo['teamID'])
        )
        recordedID = dbConsole.fetchone()[0]
        if recordedID != imageInfo['imageID']:  
            # if the image_id on record is not the same as what we got, flag the team's image
            markAsDupImage(imageInfo['teamID'], imageInfo['os'])
    else:
        # add the team to division_table
        # INSERT INTO division_table (team_id, os_id, start_time) 
        # VALUES (given_team_id, given_image_id, given_start_time);
        dbConsole.execute(
            SQL(
            """
                INSERT INTO {table} (team_id, {osID}, start_time)
                VALUES (%s, %s, %s);            
            """
            ).format(
                table=Identifier(f"{division}"),
                osID=Identifier(f"{imageInfo['os']}_id")
            ),
            (imageInfo['teamID'], imageInfo['imageID'], imageInfo['startTime'])
        )

    # add the image data into division_images 
    # INSERT INTO images_table (image_id, score, start_time, vulns_found, system_type)
    # VALUES (given_image_id, given_score, given_start_time, given_vulns_found, given_os)
    # ON CONFLICT DO UPDATE SET score = EXCLUDED.score, vulns_found = EXCLUDED.vulns_found;
    dbConsole.execute(
        SQL(
        """
            INSERT INTO {table} (image_id, score, start_time, vulns_found, system_type) 
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO UPDATE SET score = EXCLUDED.score, vulns_found = EXCLUDED.vulns_found;
        """
        ).format(
            table=Identifier(f"{division}_images")
        ), 
        (imageInfo['imageID'], imageInfo['score'], imageInfo['vulnsFound'], imageInfo['os'])
    )

    # set os_id in division table
    # UPDATE division_table SET os_id = given_image_id WHERE team_id = given_team_id;
    dbConsole.execute(
        SQL(
            "UPDATE {table} SET {column} = %s WHERE team_id = %s;"
        ).format(
            table=Identifier(f"{division}"), 
            column=Identifier(f"{imageInfo['os']}_id")
        ),
        (imageInfo['imageID'], imageInfo['teamID'])
    )

    dbConsole.commit()
    dbConsole.close()


# main loop
while True:
    imageSock, address = mySock.accept()

    thread = threading.Thread(target=handleImage, args=(imageSock))
    thread.start()

