import os
from requests import post
from json import loads, dumps
from threading import Thread
from datetime import datetime
from time import sleep
from hashlib import sha512
from base64 import b64decode

from playsound import playsound
from Cryptodome.Cipher import AES
from Cryptodome.Util.padding import unpad
import tkinter

startingInfo = {
    'logo' : "MarvinLogo",
    'key' : 'ABCabc123==',
    'vulnIV' : 'ABCabc123==', # change everytime the encryption is done again
    'engineRoot' : '/Scoring-Engine/',  # the path to the application's root from system root
    'scoring' : 'http://some.url.com/scoring/route', # web url to POST scoring data to
    'os' : 'Insert OS Name (no spaces)',
    'round' : "Enter Round Name Here"    # purely visual, should match title shown to public
}

startingInfo['keyLength'] = 16
assert startingInfo['key'], "Encryption key cannot be empty"
assert startingInfo['keyLength'] in [16, 24, 32], "Key length must be 16, 24, or 32"
startingInfo['key'] = (startingInfo['key'] * startingInfo['keyLength'])[:startingInfo['keyLength']]

if os.name=='nt':
    from win10toast import ToastNotifier
    startingInfo['engineRoot'] = f"C:{startingInfo['engineRoot']}"
    startingInfo['logo'] = f"{startingInfo['engineRoot']}{startingInfo['logo']}.ico"

    def banner(message):
        (ToastNotifier()).show_toast(
            "PolyCP Engine", message, icon_path=startingInfo['logo'])
elif os.name=='posix':
    # startingInfo['engineRoot'] = f"{startingInfo['engineRoot']}"
    startingInfo['logo'] = f"{startingInfo['engineRoot']}{startingInfo['logo']}.png"

    def banner(message):
        os.system(f"notify-send 'PolyCP Engine' '{message}' -i '{startingInfo['logo']}'")

def play(path):
    soundThread = Thread(target=playsound, args=(path, ))
    soundThread.start()

def log(content, error=''):
    def event(content, f):
        f.write(content)

    def fatalError(content, f):
        f.write(f"Engine exiting due to fatal error: {content}" )

    entries = { 
        '' : event,
        'ferror' : fatalError 
    }

    with open(startingInfo['engineRoot'] + "log.txt", "a") as logFile:
        entries[error](content, logFile)

def getTeamID():
    window = tkinter.Tk()
    window.geometry("350x100")
    # window.iconbitmap(startingInfo['logo']) # used to be the `.ico`
    window.title("Enter your Team ID")
    window.resizable(0,0)
    
    teamID= tkinter.StringVar()

    bruh = tkinter.Entry(window, textvar=teamID, width=12, font=("arial",35,"bold"))
    bruh.place(relx=0.5)
    bruh.pack()    
    
    def character_limit(teamID):
        if len(teamID.get()) > 12:
            teamID.set(teamID.get()[:12])
        elif len(teamID.get()) == 12:
            submit.config(state=tkinter.NORMAL)
        else:
            submit.config(state=tkinter.DISABLED)
        if not teamID.get().isalnum():
            teamID.set(teamID.get()[:-1])

    submit = tkinter.Button(window, text="Submit", width=12, bg="blue", borderwidth=0, fg="white", 
            command=window.destroy, font=("arial",10,"bold"), state=tkinter.DISABLED)
    submit.place(relx=0.5, rely=0.8, anchor=tkinter.CENTER)
    
    teamID.trace("w", lambda *args: character_limit(teamID))

    window.mainloop()
    return teamID.get()

class machine:
    def __init__(self, imSystem="", round="Practice Round", 
            vulnPath=(startingInfo['engineRoot'] + "vulns")):
        self.imageSystem = imSystem
        self.round = round
        self.maxScore = 0
        self.connected = False
        self.startTime = None
        self.teamID = None
        self.imageID = None
        self.Vulns = []
        self.Penalties = []

        # setting the image start time
        if not os.path.isfile(startingInfo['engineRoot'] + "image.dat"):
            persistentData = open( (startingInfo['engineRoot'] + "image.dat"), "w")
            try:
                persistentData.write(str(datetime.now().timestamp()) + '\n')
                persistentData.write(getTeamID() + '\n')
            except:
                log("Could not save image data")
            finally:
                persistentData.close()
        with open( (startingInfo['engineRoot'] + "image.dat"), "r") as persistentData:
            try:
                self.startTime = persistentData.readline().replace('\n', '')
                self.teamID = persistentData.readline().replace('\n', '')
            except:
                log("Could not read image data.")

        # create a unique image ID to detect multiple instances
        self.imageID = sha512(
            bytes(f"{self.imageSystem}{self.teamID}{self.startTime}","utf-8")
        ).hexdigest()

        # loading in scoring criteria
        with open(vulnPath, 'rb') as vulnFile:
            raw_json = unpad(
                (
                    AES.new(
                        b64decode(startingInfo['key']), 
                        AES.MODE_CBC, 
                        b64decode(startingInfo['vulnIV'])
                    )
                ).decrypt(vulnFile.read()), 
                AES.block_size
            ).decode('ascii')
        try:
            data = loads(raw_json)
        except: 
            log("Vuln data is not in JSON format", 'ferror')
            exit()

        for vuln in data['vulns']:
            self.Vulns.append(vuln)
            self.maxScore += vuln["value"] 
        for penalty in data['pens']:
            self.Penalties.append(penalty)

    def check(self, test):
        return f"{test[1]}\n" == os.popen(test[0]).read()

vm = machine(imSystem=startingInfo['os'], round=startingInfo['round'], 
            vulnPath=(startingInfo['engineRoot'] + "vulns"), penaltyPath=(startingInfo['engineRoot'] + "penalties"))

class scoredItems:
    Vulns = []
    Penalties = []
    Gain = 0
    Loss = 0

    @staticmethod
    def AddVuln(vuln):
        scoredItems.Vulns.append(vuln)
        print(f"append: vulns list now {scoredItems.Vulns}")
        scoredItems.Gain += vuln['value']
        banner("You gained points!")
        play("pointGain.wav")
    
    @staticmethod
    def RemoveVuln(vuln):
        scoredItems.Vulns.remove(vuln)
        print(f"remove: vulns list now {scoredItems.Vulns}")
        scoredItems.Gain -= vuln['value']
        banner("You messed up ...")
        play("pointLoss.wav")
    
    @staticmethod
    def AddPenalty(pen):
        scoredItems.Penalties.append(pen)
        print(f"append: pens list now {scoredItems.Penalties}")
        scoredItems.Loss += pen['value']
        banner("You messed up ...")
        play("pointLoss.wav")
    
    @staticmethod
    def RemovePenalty(pen):
        scoredItems.Penalties.remove(pen)
        print(f"remove: pens list now {scoredItems.Penalties}")
        scoredItems.Loss -= pen['value']
        banner("You gained points!")
        play("pointGain.wav")

    @staticmethod
    def updateReport(state):
        genTime = datetime.now()

        # format the found vulns and penalties in a readable html format
        penalties = ""
        for penalty in scoredItems.Penalties:
            penalties += f"{penalty['title']} - {penalty['value']} <br /> \n"
        vulns = ""
        for vuln in scoredItems.Vulns:
            vulns += f"{vuln['title']} - {vuln['value']} <br /> \n"
        
        # write what we got
        template = open("ScoreReportTemplate.html", 'r')
        try:
            page = template.read()
            # input the information the engine knows
            page = page.format( startTime=(float(state.startTime) * 1000), 
                                competition=state.round,
                                imageType=state.imageSystem,
                                timestamp=genTime,
                                connection=(
                                    f'<span style="color: green;">Connected to {startingInfo["scoring"][0]}</span>' 
                                    if vm.connected else 
                                    f'<span style="color: red;">Error: cannot connect to scoring server {startingInfo["scoring"][0]} on port {startingInfo["scoring"][1]}</span>'
                                    ),
                                score=(scoredItems.Gain - scoredItems.Loss),
                                maximumScore=state.maxScore,
                                penNum=len(scoredItems.Penalties),
                                loss=scoredItems.Loss,
                                penList=penalties,
                                vulnsFound=len(scoredItems.Vulns),
                                vulnsTotal=len(state.Vulns),
                                gain=scoredItems.Gain,
                                vulnList=vulns
                                )
            report = open(engineRoot + "ScoringReport.html", "w")
            try:
                report.write(page)
            except:
                log("Could not write updated scoring report")
            finally:
                report.close()
        except:
            log("Could not read report template: Aborting report update")
        finally:
            template.close()

def uploadState(teamID, imID, vmOS, startTime, score, foundVulns, foundPens):
    # localSocket = socket(AF_INET, SOCK_STREAM)
    # try:
    #     localSocket.connect(startingInfo['scoring'])
    data = {
        'teamID' : teamID,
        'imageID' : imID,
        'os' : vmOS,
        'startTime' : startTime,
        'score' : score,
        'vulns' : foundVulns,
        'pens' : foundPens 
    }
    try:
        post(startingInfo['scoring'], json=dumps(data))
        print(f"sent data {data} to {startingInfo['scoring']}")
        return True
    except:
        return False

while True:
    for vuln in vm.Vulns:
        vul = { "title": vuln['title'], "value": vuln['value'] }
        if vul in scoredItems.Vulns:
            # already solved case
            if not vm.check(vuln['test']):
                # remove the vul if no longer true
                scoredItems.RemoveVuln(vul)
        else:
            # not-yet-solved case
            if vm.check(vuln['test']):
                # add the vuln if they solved it
                scoredItems.AddVuln(vul)
    # again for penalties
    for penalty in vm.Penalties:
        pen = { "title": penalty['title'], "value": penalty['value'] }
        if pen in scoredItems.Penalties:
            if not vm.check(penalty['test']):
                scoredItems.RemovePenalty(pen)
        else:
            if vm.check(penalty['test']):
                scoredItems.AddPenalty(pen)
    scoredItems.updateReport(vm)
    print(f"Calling upload function")
    vm.connected = uploadState(vm.teamID, vm.imageID, vm.imageSystem, vm.startTime,
        (scoredItems.Gain - scoredItems.Loss), len(scoredItems.Vulns),
        len(vm.Vulns), len(scoredItems.Penalties))
    sleep(30)
