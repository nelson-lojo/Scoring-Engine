from datetime import datetime
from orator import Model
from orator.orm import belongs_to, belongs_to_many
from competition import Competition


class Team(Model):

    def __init__(self, teamID: str, start: datetime):
        self.uid = teamID
        self.startTime = start

        self.endTime = datetime.fromtimestamp(0)
        self.score = 0

    @belongs_to_many
    def competition(self):
        return Competition

