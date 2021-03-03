import os
from socket import socket, AF_INET, SOCK_STREAM
from json import loads
from threading import Thread
from datetime import datetime
from time import sleep
from hashlib import sha512

from playsound import playsound
from Cryptodome.Cipher import AES
import tkinter

startingInfo = {
    'logo' : "MarvinLogo",
    'key' : b'Die-go is hella gay lmao', # must be 16, 24, or 32 chars
    'vulnNonce' : b'\xd0\x7b\x29\x9f\x37\xda\x79\x1c\x95\x91\x6a\xd9\x30\x7a\x1f\x13',     # change everytime the encryption is done again
    'penNonce' : b'\x09\x0f\xff\xdc\x27\xff\x31\x04\x84\x6f\x49\x36\x5d\xc1\x3e\x9b',      # change everytime the encryption is done again
    'engineRoot' : 'home/jeremy/Documents/Scoring-Engine/host/',  # the path to the application's root from system root
    'scoreboard' : ('18.224.165.244', int('6969')),
    'os' : 'GenericSystem20.04',     # cannot have spaces
    'round' : "Practice Round"       # purely visual, but should also 
}

logo = startingInfo['logo']
engineRoot = startingInfo['engineRoot']

if os.name=='nt':
    from win10toast import ToastNotifier
    engineRoot = f"C:/{engineRoot}"
    logo += '.ico'

    def banner(message):
        (ToastNotifier()).show_toast(
            "PolyCP Engine", message, icon_path=(engineRoot + logo))
elif os.name=='posix':
    engineRoot = f"/{engineRoot}"
    logo += '.png'

    def banner(message):
        os.system(
            f"notify-send 'PolyCP Engine' '{message}' -i '{engineRoot + logo}'")

def play(path):
    Thread(target=playsound, args=(path, )).start()

def log(content, error=''):
    logFile = open(engineRoot + "log.txt", "a")

    def event(content):
        logFile.write(content)

    def fatalError(content):
        logFile.write(f"Engine exiting due to fatal error: {content}" )

    contentKey = { 
                    '' : event,
                    'ferror' : fatalError 
                 }
    contentKey[error]()
    logFile.close()

def getTeamID():
    window = tkinter.Tk()
    window.geometry("350x100")
    #window.iconbitmap(engineRoot + startingInfo['logo'] + '.ico')
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
            vulnPath=(engineRoot + "vulns"), penaltyPath=(engineRoot + "penalties")):
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
        if not os.path.isfile(engineRoot + "image.dat"):
            persistentData = open( (engineRoot + "image.dat"), "w")
            try:
                persistentData.writelines(str(datetime.utcnow().timestamp()))
                persistentData.writelines(getTeamID())
            except:
                log("Could not write image image data to file")
            finally:
                persistentData.close()
        persistentData = open( (engineRoot + "image.dat"), "r")
        try:
            self.startTime = persistentData.readline()
            self.teamID = persistentData.readline()
        except:
            log("Could not read image data.")
        finally:
            persistentData.close()

        # create a unique image ID to detect multiple instances
        self.imageID = sha512(
            bytes(
                f"{self.imageSystem}{self.teamID}{self.startTime}","utf-8"
                )).hexdigest()

        # loading in vulns
        vulnFile = open(vulnPath, 'rb')
        vulnData = ( AES.new(startingInfo['key'], AES.MODE_EAX, nonce=startingInfo['vulnNonce']) 
                        ).decrypt(vulnFile.read())
        vulnFile.close()
        try:
            vulns = loads(vulnData.decode("utf-8"))
            for vuln in vulns:
                self.Vulns.append(vuln)
                self.maxScore += vuln["value"]
            del vulns
        except: 
            log("Vuln data is not in JSON format", 'ferror')
            exit()

        # loading in penalties
        penFile = open(penaltyPath, 'rb')
        penData = ( AES.new(startingInfo['key'], AES.MODE_EAX, nonce=startingInfo['penNonce']) 
                    ).decrypt(penFile.read())
        penFile.close()
        try:
            penalties = loads(penData.decode("utf-8"))
            for penalty in penalties:
                self.Penalties.append(penalty)
            del penalties
        except: 
            log("Penalty data is not in JSON format")
            exit()

    def check(self, test):
        return f"{test[1]}\n" == os.popen(test[0]).read()

vm = machine(imSystem=startingInfo['os'], round=startingInfo['round'], 
            vulnPath=(engineRoot + "vulns"), penaltyPath=(engineRoot + "penalties"))

class scoredItems:
    Vulns = []
    Penalties = []
    Gain = 0
    Loss = 0

    @staticmethod
    def AddVuln(title, value):
        scoredItems.Vulns.append({"title":title, "value":value})
        scoredItems.Gain += value
        banner("You gained points!")
        play("pointGain.wav")
    
    @staticmethod
    def RemoveVuln(title, value):
        scoredItems.Vulns.remove({"title":title, "value":value})
        scoredItems.Gain -= value
        banner("You messed up ...")
        play("pointLoss.wav")
    
    @staticmethod
    def AddPenalty(title, value):
        scoredItems.Penalties.append({"title":title, "value":value})
        scoredItems.Loss += value
        banner("You messed up ...")
        play("pointLoss.wav")
    
    @staticmethod
    def RemovePenalty(title, value):
        scoredItems.Penalties.remove({"title":title, "value":value})
        scoredItems.Loss -= value
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
            page = page.format( startTime=state.startTime, 
                                competition=state.round,
                                imageType=state.imageSystem,
                                timestamp=genTime,
                                connection=(
                                    f'<span style="color: green;">Connected to {startingInfo["scoreboard"][0]}</span>' 
                                    if vm.connected else 
                                    f'<span style="color: red;">Error: cannot connect to scoring server {startingInfo["scoreboard"][0]} on port {startingInfo["scoreboard"][1]}</span>'
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

def uploadState(teamID, imID, vmOS, startTime, score, foundVulns):
    localSocket = socket(AF_INET, SOCK_STREAM)
    try:
        localSocket.connect(startingInfo['scoreboard'])

        msg = f"{teamID} {imID} {vmOS} {startTime} {score} {foundVulns}"
        print(f"sending message '{msg}' to {startingInfo['scoreboard'][0]}:{startingInfo['scoreboard'][1]}")
        localSocket.send(bytes(msg, "utf-8"))
        print(f"\tsent!")
        if not vm.connected:
            vm.connected = True
    except:
        if vm.connected:
            vm.connected = False
    finally:
        sleep(1)
        localSocket.close()

while True:
    for vuln in vm.Vulns:
        if vuln in scoredItems.Vulns:
            # already solved case
            if not vm.check(vuln['test']):
                # remove the vuln if no longer true
                scoredItems.RemoveVuln(vuln['title'], vuln['value'])
        else:
            # not-yet-solved case
            if vm.check(vuln['test']):
                # add the vuln if they solved it
                scoredItems.AddVuln(vuln['title'], vuln['value'])
    # again for penalties
    for penalty in vm.Penalties:
        if penalty in scoredItems.Penalties:
            if not vm.check(penalty['test']):
                scoredItems.RemovePenalty(penalty['title'], penalty['value'])
        else:
            if vm.check(penalty['test']):
                scoredItems.AddPenalty(penalty['title'], penalty['value'])
    scoredItems.updateReport(vm)
    # print(f"")
    uploadState(vm.teamID, vm.imageID, vm.imageSystem, vm.startTime,
        (scoredItems.Gain - scoredItems.Loss), len(scoredItems.Vulns))
    sleep(30)

#####
    # [
    #  {
    #    "test": ["powershell -c \"(glu nalso).enabled\"", "True"],
    #    "title": "User Nasloon is enabled",
    #    "value": 10
    #  },
    #  {
    #    "test": ["powershell -c \''\", ""],
    #    "title": "",
    #    "value": 10
    #  },
    #  {
    #    "test": ["powershell -c \"-not (glu administrator).enabled\"", "False"],
    #    "title": "Removed Unauthorized Admin",
    #    "score": 10
    #  }
    # ]


    # encrypt a json file:
    # from Cryptodome.Cipher import AES
    # key = b'Die-go is hella gay lmao'
    # cipher = AES.new(key, AES.MODE_EAX)
    # (pls check nonce {cipher.nonce})
    # ciphertext, tag = cipher.encrypt_and_digest(data_string)
    # then write ciphertext to the file (vulns or penalties)