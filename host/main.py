import json, os, socket
from Cryptodome.Cipher import AES
from datetime import datetime
from time import sleep
from hashlib import sha512

startingInfo = {
    'logo' : "MarvinLogo",
    'key' : b'Die-go is hella gay lmao', # must be 16, 24, or 32 chars
    'vulnNonce' : None,     # change everytime the encryption is done again
    'penNonce' : None,      # change everytime the encryption is done again
    'engineRoot' : 'ScoringEngine/',
    'scoreboard' : ('ip/dns', int('port')),
    'os' : 'GenericSystem18.04',     # cannot have spaces
    'round' : "Practice Round"       # purely visual
}

logo = startingInfo['logo']
engineRoot = startingInfo['engineRoot']

if os.name=='nt':
    from win10toast import ToastNotifier
    import winsound
    engineRoot = f"C:/{engineRoot}"
    logo += '.ico'

    def play(path):
        winsound.PlaySound(path, winsound.SND_ALIAS)

    def banner(message):
        (ToastNotifier()).show_toast(
            "PolyCP Engine", message, icon_path=(engineRoot + logo))
elif os.name=='posix':
    os.system("sudo apt install -y sox")
    engineRoot = f"/{engineRoot}"
    logo += '.png'

    def play(path):
        os.system(f"play {engineRoot + path}")

    def banner(message):
        os.system(
            f"notify-send 'PolyCP Engine' '{message}' -i '{engineRoot + logo}'")

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
    pass

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
                persistentData.write(str(datetime.now().utcnow()))
                persistentData.write(getTeamID())
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
                        ).decrypt(vulnFile.readlines())
        vulnFile.close()
        try:
            with json.loads(vulnData.decode("utf-8")) as vulns:
                for vuln in vulns:
                    self.Vulns += vuln
                    self.maxScore += vuln["value"]
        except: 
            log("Vuln data is not in JSON format", 'ferror')
            exit()

        # loading in penalties
        penFile = open(penaltyPath, 'rb')
        penData = ( AES.new(startingInfo['key'], AES.MODE_EAX, nonce=startingInfo['penNonce']) 
                    ).decrypt(penFile.readlines())
        penFile.close()
        try:
            with json.loads(penData.decode("utf-8")) as penalties:
                for penalty in penalties:
                    self.Penalties += penalty
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
        scoredItems.Vulns += {"title":title, "value":value}
        scoredItems.Gain += value
        banner("You gained points!")
        play("pointGain.song")
    
    @staticmethod
    def RemoveVuln(title, value):
        scoredItems.Vulns.remove({"title":title, "value":value})
        scoredItems.Gain -= value
        banner("You messed up ...")
        play("pointLoss.song")
    
    @staticmethod
    def AddPenalty(title, value):
        scoredItems.Penalties += {"title":title, "value":value}
        scoredItems.Loss += value
        banner("You messed up ...")
        play("pointLoss.song")
    
    @staticmethod
    def RemovePenalty(title, value):
        scoredItems.Penalties.remove({"title":title, "value":value})
        scoredItems.Loss -= value
        banner("You gained points!")
        play("pointGain.song")

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
            page = template.readlines()
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

def upload(teamID, imID, vmOS, startTime, score, foundVulns):
    localSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        localSocket.connect(startingInfo['scoreboard'])
        localSocket.send(f"{teamID} {imID} {vmOS} {startTime} {score} {foundVulns}")
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
    upload(vm.teamID, vm.imageID, vm.imageSystem, vm.startTime
        (scoredItems.Gain - scoredItems.Loss), len(scoredItems.Vulns))
    scoredItems.updateReport(vm)
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