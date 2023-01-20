from datetime import datetime
from orator import Model
from orator.orm.utils import belongs_to
from team import Team

class Image(Model):

    def __init__(self, os: str, score: int, start: datetime, vulns: int, pens: int):
        self.os = os
        self.score = score
        self.startTime = start
        self.multipleInstances = False
        self.timeExceeded = False

    def endTime(self):
        # can be relegated to the db
        newest = max(self.reports, key=(lambda report: report.time))
        return newest.time

    @belongs_to
    def team(self):
        return Team
