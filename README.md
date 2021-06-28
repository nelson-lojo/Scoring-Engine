# PolyCP Scoring Engine

## Table of Contents
- About
- Features
- Setup

## About
This is an imitation of the Cyberpatriot Scoring Engine and intended to enable smaller organizations to train incoming members.


## Features
- Uses MongoDB to store team information
- Stores vulnerability and penalty info as AES Encrypted JSON in competitor images to improve performance and allow unlimited customization
- Supports multiple concurrent competitions, each split by divisions

## Setup

### For each image:
1. Create a json file with all scoring criteria and make a copy of the `host/` directory
2. Run the `encrypt.py` script on it: `python3 encrypt.py <json vuln file>` and save the output IV and key
3. Move the produced file to the copied `host/` directory
4. Set the parameters in the copied `host/main.py`
    - these are the elements in the dictionary at the top of the file
5. Copy the contents of the configured `host/` directory into the desired engine root
6. Set a scheduled task to execute `<scoring engine root>/main.py` regularly

### For the scoring server
1. Configure the information in `server-side/data.py`
2. Copy both the configured `data.py` and `server-side/scoring-server/scoring_server.py` to the destination machine (in the same directory)
3. Run `scoring_server.py`: `python3 scoring_server.py`

### For the scoreboard server
1. Configure the information in `server-side/data.py`
    - if you've already set up the scoring server, you can update the `info` dict and reuse it
2. Copy the configured `data.py` to `server-side/scoreboard-server/` and move `scoreboard-server/` to the desired machine
3. Run `web_server.py` : `python3 web_server.py`

## Possible Expansions
- Prepare repository for compilation in GraalVM
- Scoreboard 
    - Implement search for competitions and divisions 
- Setup UI
    - Create GUI for initializing server-side components
        - create data.py
        - install mongod
        - compile main python files into native binary
    - Create vuln and penalty file UI
        - UI needs to abstractify command writing to allow clients with no CLI experience to create images
        - use Java + GraalVM 
    - Add ability to automatically create initialized VMs
- Write the user manual (this readme)
    - make About pretty
    - expand Features
        - and make it pretty
    - write the Setup section to guide installation
        - on both server side and image initialization



