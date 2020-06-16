import json, os
from Cryptodome.Cipher import AES
from datetime import datetime
from time import sleep

logo = "MarvinLogo"
key = b'Die-go is hella gay lmao'  # must be 16, 24, or 32 chars
vulnNonce = None                   # change everytime the encryption is done again
penNonce = None
engineRoot = 'ScoringEngine/'

if os.name=='nt':
    from win10toast import ToastNotifier
    import winsound
    engineRoot = f"C:/{engineRoot}"
    logo += '.ico'

    def play(path):
        winsound.PlaySound(path, winsound.SND_ALIAS)

    def banner(message):
        (ToastNotifier()).show_toast("PolyCP Engine", message, icon_path=(engineRoot + logo))
elif os.name=='posix':
    os.system("sudo apt install -y sox")
    engineRoot = f"/{engineRoot}"
    logo += '.png'

    def play(path):
        os.system(f"play {engineRoot + path}")

    def banner(message):
        os.system(f"notify-send 'PolyCP Engine' '{message}' -i '{engineRoot + logo}'")

def check(test):
    return f"{test[1]}\n"==os.popen(test[0]).read()

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

class machine:
    ImageType = ""
    Round = ""
    maxScore = 0
    startTime = None
    Vulns = []
    Penalties = []
    def __init__(self, imType="", round="Practice Round", vulnPath=(engineRoot + "vulns"), penaltyPath=(engineRoot + "penalties")):
        self.ImageType = imType
        self.Round = round

        # setting the image start time
        if not os.path.isfile(engineRoot + "imageTime.dat"):
            startTimeLog = open( (engineRoot + "imagetime.dat"), "w")
            try:
                startTimeLog.write(str(datetime.now().utcnow()))
            except:
                log("Could not write image start time to file")
            finally:
                startTimeLog.close()
        startTimeLog = open( (engineRoot + "imagetime.dat"), "r")
        try:
            self.startTime = startTimeLog.readlines()
        except:
            log("Could not read image start time.")
        finally:
            startTimeLog.close()

        # loading in vulns
        vulnFile = open(vulnPath, 'rb')
        vulnData = ( AES.new(key, AES.MODE_EAX, nonce=vulnNonce) ).decrypt(vulnFile.readlines())
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
        penData = ( AES.new(key, AES.MODE_EAX, nonce=penNonce) ).decrypt(penFile.readlines())
        penFile.close()
        try:
            with json.loads(penData.decode("utf-8")) as penalties:
                for penalty in penalties:
                    self.Penalties += penalty
        except: 
            log("Penalty data is not in JSON format")
            exit()

vm = machine()

class scoringTemplate:
    Vulns = []
    Penalties = []
    Gain = 0
    Loss = 0
    def __init__(self):
        self.Gain = 0
    def AddVuln(self, title, value):
        self.Vulns += {"title":title, "value":value}
        self.Gain += value
        banner("You gained points!")
        play("pointGain.song")
    def RemoveVuln(self, title, value):
        self.Vulns.remove({"title":title, "value":value})
        self.Gain -= value
        banner("You messed up ...")
        play("pointLoss.song")
    def AddPenalty(self, title, value):
        self.Penalties += {"title":title, "value":value}
        self.Loss += value
        banner("You messed up ...")
        play("pointLoss.song")
    def RemovePenalty(self, title, value):
        self.Penalties.remove({"title":title, "value":value})
        self.Loss -= value
        banner("You gained points!")
        play("pointGain.song")

scoredItems = scoringTemplate()

def updateReport(items, state):
    genTime = datetime.now()
    penalties = ""
    for penalty in items.Penalties:
        penalties += f"{penalty['title']} - {penalty['value']} <br /> \n"
    vulns = ""
    for vuln in items.Vulns:
        vulns += f"{vuln['title']} - {vuln['value']} <br /> \n"
    page = f"""
<!DOCTYPE html>
<html>
    <head>
        <title>PolyCP Scoring Report</title>
        <style>
            body {{
                background-color: #336699;
                font-family: Arial, Verdana, sans-serif;
            }}
            #content {{
                background-color: white;
                width: 70%;
                margin-left: auto;
                margin-right: auto;
                padding: 10px;
                height: 100%;
				border-radius: 12px;
            }}
            #barz {{
                text-align: center;
                line-height: 16px;
                margin: 0;
            }}
            img {{
                height: 180px;
            }}
        </style>
        <script>
            var imageStartTime = new Date({vm.startTime});
            setInterval(function() {{
                var now = new Date().getTime();
                var hours = Math.floor((now - imageStartTime) / (1000 * 60 * 60)) 
                var mins = Math.floor((now - imageStartTime) % (1000 * 60 * 60) / (1000 * 60))
                document.getElementById("imageTimer").innerHTML = hours + ":" + mins 
            }}, 1000)
        </script>
    </head>
    <body>
        <div id="content">
            <div id="barz">
                <img src="CYBERPATRIOT_Logo_black.png"> <br />
                <h1 id="imageTitle">PolyCP {state.Round} {state.ImageType} Image</h1> <br />
                <h2 id="genTime">Report Generated At: {genTime}</h2> <br />
                <h3>Approximate Image running Time: <span id="imageTimer"></span> </h3>
                <h2 id="score">{items.Gain - items.Loss} out of {state.maxScore} points recieved</h2> <br />
            </div>
            <br /><br /><br />
            <div id="main">
                <b>{len(items.Penalties)} penalties assessed, for a loss of {items.Loss} points:</b> <br />
                <br />
                <span style="color: red;"> {penalties} </span>
                <br /><br />
                <br />
                <b>{len(items.Vulns)} out of {len(state.Vulns)} scored security issues fixed, for a gain of {items.Gain} points: </b> <br />
                <br />
                {vulns}
                <br />
                <br />
            </div>
        </div>
    </body>
</html>"""
    report = open(engineRoot + "ScoringReport.html", "w")
    report.write(page)
    report.close()

while True:
    for vuln in vm.Vulns:
        if vuln in scoredItems.Vulns:
            # already solved case
            if not(check(vuln['test'])):
                # remove the vuln if no longer true
                scoredItems.RemoveVuln(vuln['title'], vuln['value'])
        else:
            # not-yet-solved case
            if check(vuln['test']):
                # add the vuln if they solved it
                scoredItems.AddVuln(vuln['title'], vuln['value'])
    # again for penalties
    for penalty in vm.Penalties:
        if penalty in scoredItems.Penalties:
            if not(check(penalty['test'])):
                scoredItems.RemovePenalty(penalty['title'], penalty['value'])
        else:
            if check(penalty['test']):
                scoredItems.AddPenalty(penalty['title'], penalty['value'])
    updateReport(scoredItems, vm)
    sleep(30)

###
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