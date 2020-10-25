import bisect
import random
import math
import sys
import time
from energium.kit import Agent
from energium.game_constants import GAME_CONSTANTS, DIRECTIONS
ALL_DIRECTIONS = [DIRECTIONS.EAST, DIRECTIONS.NORTH,
                  DIRECTIONS.WEST, DIRECTIONS.SOUTH]

BREAKDOWN_TURNS = GAME_CONSTANTS["PARAMETERS"]["BREAKDOWN_TURNS"] * GAME_CONSTANTS["PARAMETERS"]["BREAKDOWN_MAX"]
UNIT_COST = GAME_CONSTANTS["PARAMETERS"]["UNIT_COST"]
# Create new agent
agent = Agent()

# initialize agent
agent.initialize()

global game_map
game_map = agent.map
WIDTH = game_map.width
HEIGHT = game_map.height

DIRS = [[0, 1], [0, -1], [1, 0], [-1, 0], [0, 0]]

def move_to_dir(move):
    if move[0] == 0 and move[1] == 1:
        return DIRECTIONS.SOUTH
    elif move[0] == 0 and move[1] == -1:
        return DIRECTIONS.NORTH
    elif move[0] == 1 and move[1] == 0:
        return DIRECTIONS.EAST
    elif move[0] == -1 and move[1] == 0:
        return DIRECTIONS.WEST
    return None

global breakable_map
breakable_map = None
global base_map
base_map = [[False for i in range(WIDTH)] for j in range(HEIGHT)]
global my_bases

# global score_map
# score_map = [[game_map.get_tile(i, j).energium for i in range(WIDTH)] for j in range(HEIGHT)]
# for t in range(100):
#     for a in range(WIDTH):
#         for b in range(HEIGHT):
#             s = 0
#             for dx, dy in DIRS:
#                 x = dx + a
#                 y = dy + b
#                 if x > 0 and x < WIDTH and y > 0 and y < HEIGHT:
#                     s += score_map[y][x]
#             score_map[b][a] = s/4

def set_breakable_map(my_units, enemy_units, enemy_bases):
    global breakable_map
    breakable_map = [[0 for i in range(WIDTH)] for j in range(HEIGHT)]

    for e in my_units:
        breakable_map[e.y][e.x] = e.last_repair_turn
        # So units will move out of the way for other units of higher priority.
        for dx, dy in DIRS:
            x = e.x + dx
            y = e.y + dy
            if x > -1 and y > -1 and x < WIDTH and y < HEIGHT:
                breakable_map[y][x] = e.last_repair_turn
    for e in enemy_units:
        breakable_map[e.y][e.x] = e.last_repair_turn
    for e in enemy_bases:
        breakable_map[e.y][e.x] = GAME_CONSTANTS["PARAMETERS"]["MAX_TURNS"]

def set_base_map(my_bases):
    for e in my_bases:
        base_map[e.y][e.x] = True

class State(object):
    def __init__(self, unit, energy, moves=[], broken=False):
        # Units should just be a list of positions + repair turns
        # unit = [x, y, repair_turn, current_turn]
        #print(unit, file=sys.stderr)
        self.unit = unit
        self.energy = energy
        self.moves = moves
        self.broken = broken
        if unit[3] - unit[2] >= BREAKDOWN_TURNS:
            self.broken = True
            self.energy -= UNIT_COST

    def score(self):
        return self.energy # + score_map[self.unit[1]][self.unit[0]]

    def next_states(self):
        if self.broken:
            yield self
        else:
            for dx, dy in DIRS:
                x = self.unit[0] + dx
                y = self.unit[1] + dy
                if x > -1 and y > -1 and x < WIDTH and y < HEIGHT:
                    broken = self.broken or breakable_map[y][x] > self.unit[2]
                    u = self.unit[:]
                    u[0] += dx
                    u[1] += dy
                    u[3] += 1
                    if base_map[y][x]:
                        u[2] = u[3]
                    new_state = State(
                        u, self.energy + game_map.get_tile(x, y).energium, self.moves + [[dx, dy]], broken)
                    yield new_state


def beamsearch(states, start_time, max_time=0.1, beamwidth=400):
    depth = 0
    while time.time() - start_time < max_time:
        depth += 1
        best_states = []
        lowest = None
        l = 0
        for state in states:
            for s in state.next_states():
                if l < beamwidth:
                    if lowest is None:
                        lowest = s.energy
                    else:
                        lowest = min(lowest, s.energy)
                    bisect.insort(best_states, [-s.score(), random.random(), s])
                    l += 1
                elif s.energy > lowest:
                    lowest = s.energy
                    best_states.pop()
                    bisect.insort(best_states, [-s.score(), random.random(), s])
        states = [b[-1] for b in best_states]
    #print(depth, file=sys.stderr)
    return states[0]


# Once initialized, we enter an infinite loop
base_map_set = False
while True:

    # wait for update from match engine
    agent.update()

    commands = []

    # player is your player object, opponent is the opponent's
    player = agent.players[agent.id]
    opponent = agent.players[(agent.id + 1) % 2]

    # all your collectorunits
    my_units = player.units

    # all your bases
    my_bases = player.bases

    if not base_map_set:
        base_map_set = True
        set_base_map(my_bases)

    enemy_units = opponent.units
    enemy_bases = opponent.bases

    # use print("msg", file=sys.stderr) to print messages to the terminal or your error log.
    # normal prints are reserved for the match engine. Uncomment the lines below to log something
    # print('Turn {} | ID: {} - {} bases - {} units - energium {}'.format(agent.turn, player.team, len(my_bases), len(my_units), player.energium), file=sys.stderr)

    ### AI Code goes here ###

    set_breakable_map(my_units, enemy_units, my_bases)

    # Let your creativity go wild. Feel free to change this however you want and
    # submit it as many times as you want to the servers

    # spawn unit until we have 4 units
    if len(my_units) < 4 and player.energium >= GAME_CONSTANTS["PARAMETERS"]["UNIT_COST"]:
        commands.append(my_bases[0].spawn_unit())

    # iterate over all of our collectors and make them do something
    for unit in my_units:
        state = State([unit.x, unit.y, unit.last_repair_turn, unit.match_turn], 0)
        moves = beamsearch([state], time.time(), 0.5/len(my_units)).moves
        if(len(moves) > 0):
            dir = move_to_dir(moves[0])
            if dir is not None:
                commands.append(unit.move(dir))

    ### AI Code ends here ###

    # submit commands to the engine
    print(','.join(commands))

    # now we end our turn
    agent.end_turn()
