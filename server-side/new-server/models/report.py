from datetime import datetime
from orator import Model
from image import Image

class Report(Model):

    def __init__(self, **kwargs):
        self.teamID = kwargs['teamID']
        self.imageID = kwargs['imageID']
        self.os = kwargs['os']
        self.startTime = kwargs['startTime']
        self.score = kwargs['score']
        self.vulns = kwargs['vulns']
        self.pens  = kwargs['pens']
        self.timestamp = datetime.now()
        
    @belongs_to
    def image(self):
        return Image
