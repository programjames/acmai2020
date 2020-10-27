from typing import List
from .position import Position
from .game_constants import GAME_CONSTANTS, DIRECTIONS
import math
import sys
class Base:
    def __init__(self, team: int, x, y):
        self.team = team
        self.pos = Position(x, y)
        self.x = x
        self.y = y

    def spawn_unit(self):
        return 'c {} {}'.format(self.pos.x, self.pos.y)

def dir_to_move(dir):
    if dir == DIRECTIONS.SOUTH:
        return [0, 1]
    elif dir == DIRECTIONS.NORTH:
        return [0, -1]
    elif dir == DIRECTIONS.EAST:
        return [1, 0]
    elif dir == DIRECTIONS.WEST:
        return [-1, 0]
    return None

class Unit:
    def __init__(self, team: int, unitid: int, x, y, last_repair_turn, turn):
        self.team = team
        self.id = unitid
        self.pos = Position(x, y)
        self.x = x
        self.y = y
        self.last_repair_turn = last_repair_turn
        self.match_turn = turn
        self.has_moved = False

    def get_breakdown_level(self):
        """
        returns the breakdown level of this unit
        """
        return (self.match_turn - self.last_repair_turn) / GAME_CONSTANTS['PARAMETERS']['BREAKDOWN_TURNS'];
    def move(self, dir):
        self.has_moved = True
        dx, dy = dir_to_move(dir)
        self.pos = Position(self.x + dx, self.y + dy)
        self.x += dx
        self.y += dy
        return 'm {} {}'.format(self.id, dir)

    def copy(self):
        return Unit(self.team, self.id, self.x, self.y, self.last_repair_turn, self.turn)

class Player:
    energium: int
    team: int
    units: List[Unit]
    bases: List[Base]
    def __init__(self, team):
        self.team = team
        self.bases = []
        self.units = []
        self.energium = 0
