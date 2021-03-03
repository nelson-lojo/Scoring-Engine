# PolyCP Scoring Engine

## Table of Contents
- About
- Features
- Setup


## Todo list
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


## About
This is an imitation of the Cyberpatriot Scoring Engine and intended to enable smaller organizations to train incoming members.


## Features
- Uses MongoDB to store team information
- Stores vulnerability and penalty info as AES Encrypted JSON in competitor images to improve performance and allow unlimited customization
- Supports multiple concurrent competitions, each split by divisions

## Setup
