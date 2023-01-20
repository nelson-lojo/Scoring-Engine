from typing import List
from orator import Model
from orator.orm import has_many
from team import Team


class Competition(Model):

    def __init__(self, name: str, division: str, teamCount: int, images: List[str]):
        self.name = name
        self.division = division
        self.teamCount = teamCount
        self.images = images

    @has_many
    def teams(Team):
        return Team