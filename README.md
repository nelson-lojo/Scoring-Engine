# PolyCP Scoring Engine

## Table of Contents
- About
- Features
- Setup


## Todo list
- Scoreboard 
    - Complete interface
    - Implement data transfer between web client and score-keeping db
- Setup UI
    - Create GUI for initializing server-side components
    - Create vuln and penalty file UI
    - Add ability to automatically create initialized VMs


## About
This is an imitation of the Cyberpatriot Scoring Engine and intended to enable smaller organizations to train incoming members.


## Features
- Uses MongoDB to store team information
- Stores vulnerability and penalty info as AES Encrypted JSON in competitor images to improve performance and allow unlimited customization
- Supports multiple concurrent competitions, each split by divisions