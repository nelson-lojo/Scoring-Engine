# image runtime
# fix audio issues
# 
# teach how to use encyption
# send compiled executable


import json, os, gc
from Cryptodome.Cipher import AES
from datetime import datetime
from time import sleep

logo = "MarvinLogo.png"
key = b'Die-go is hella gay lmao'  # must be 16, 24, or 32 chars
vulnNonce = ''                     # change everytime the encryption is done again
penNonce = ''

if os.name=='nt':
    from win10toast import ToastNotifier
    import winsound
    engineRoot = "C:/ScoringEngine/"

    def play(path):
        winsound.PlaySound(path, winsound.SND_ALIAS)

    def banner(message):
        bubbleBase = ToastNotifier()
        bubbleBase.show_toast("PolyCP Engine", message, icon_path=(engineRoot + logo))

    def check(test):
        return f"{test[1]}\n"==os.popen(test[0]).read()
elif os.name=='posix':
    os.system("sudo apt install -y sox")
    engineRoot = "/ScoringEngine/"

    def play(path):
        os.system(f"play {engineRoot + path}")

    def banner(message):
        os.system(f"notify-send 'PolyCP Engine', {message} -i {engineRoot + logo}")

    def check(test):
        return test[1]==os.popen(test[0]).read()
    
class machine:
    ImageType = ""
    Round = ""
    maxScore = 0
    Vulns = []
    Penalties = []
    def __init__(self, imType="", round="Practice Round", vulnPath=(engineRoot + "vulns"), penaltyPath=(engineRoot + "penalties")):
        self.ImageType = imType
        self.Round = round
        # loading in vulns
        vulnFile = open(vulnPath, 'rb')
        vulnData = ( AES.new(key, AES.MODE_EAX, nonce=vulnNonce) ).decrypt(vulnFile.readlines())
        vulnFile.close()
        with json.loads(vulnData.decode("utf-8")) as vulns:
            for vuln in vulns:
                self.Vulns += vuln
                self.maxScore += vuln["value"]
        # loading in penalties
        penFile = open(penaltyPath, 'rb')
        penData = ( AES.new(key, AES.MODE_EAX, nonce=penNonce) ).decrypt(penFile.readlines())
        penFile.close()
        with json.loads(penData.decode("utf-8")) as penalties:
            for penalty in penalties:
                self.Penalties += penalty
  
state = machine()

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

def updateReport():
    genTime = datetime.now()
    penalties = ""
    for penalty in scoredItems.Penalties:
        penalties += f"{penalty['title']} - {penalty['value']} <br /> \n"
    vulns = ""
    for vuln in scoredItems.Vulns:
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
    </head>
    <body>
        <div id="content">
            <div id="barz">
                <img src="CYBERPATRIOT_Logo_black.png"> <br />
                <h1 id="imageTitle">PolyCP {state.Round} {state.ImageType} Image</h1> <br />
                <h2 id="genTime">Report Generated At: {genTime}</h2> <br />
                <h2 id="score">{scoredItems.Gain - scoredItems.Loss} out of {state.maxScore} points recieved</h2> <br />
            </div>
            <br /><br /><br />
            <div id="main">
                <b>{len(scoredItems.Penalties)} penalties assessed, for a loss of {scoredItems.Loss} points:</b> <br />
                <br />
                <span style="color: red;"> {penalties} </span>
                <br /><br />
                <br />
                <b>{len(scoredItems.Vulns)} out of {len(state.Vulns)} scored security issues fixed, for a gain of {scoredItems.Gain} points: </b> <br />
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
    for vuln in state.Vulns:
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
    for penalty in state.Penalties:
        if penalty in scoredItems.Penalties:
            if not(check(penalty['test'])):
                scoredItems.RemovePenalty(penalty['title'], penalty['value'])
        else:
            if check(penalty['test']):
                scoredItems.AddPenalty(penalty['title'], penalty['value'])
    updateReport()
    sleep(60)
  
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