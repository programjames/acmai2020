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
GAME_LENGTH = GAME_CONSTANTS["PARAMETERS"]["MAX_TURNS"]
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
NEIGHBORS = [[0, 1], [0, -1], [1, 0], [-1, 0]]

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
global unit_map
unit_map = None
global base_map
base_map = [[False for i in range(WIDTH)] for j in range(HEIGHT)]
global my_bases

global score_map
energies = [[game_map.get_tile(i, j).energium for i in range(WIDTH)] for j in range(HEIGHT)]
score_map = [[energies[j][i] for i in range(WIDTH)] for j in range(HEIGHT)]
score_map_2 = [[energies[j][i] for i in range(WIDTH)] for j in range(HEIGHT)]
def set_score_map(unit=None, max_time=0.05):
    global score_map, energies
    #score_map = [[energies[j][i] for i in range(WIDTH)] for j in range(HEIGHT)]
    t = time.time()
    depth = 0
    repair_turn = 0 if unit is None else unit.last_repair_turn
    while time.time() - t < max_time:
        depth += 1
        for a in range(WIDTH):
            for b in range(HEIGHT):
                s = 0
                for dx, dy in NEIGHBORS:
                    x = dx + a
                    y = dy + b
                    if x >= 0 and x < WIDTH and y >= 0 and y < HEIGHT and breakable_map[y][x] <= repair_turn:
                        s = max(s, score_map[y][x])
                score_map[b][a] = energies[b][a] + 0.9 * s
def set_score_map_2(unit=None, max_time=0.05):
    global score_map_2, energies
    #score_map_2 = [[energies[j][i] for i in range(WIDTH)] for j in range(HEIGHT)]
    t = time.time()
    depth = 0
    repair_turn = 0 if unit is None else unit.last_repair_turn
    while time.time() - t < max_time:
        depth += 1
        for a in range(WIDTH):
            for b in range(HEIGHT):
                s = 0
                for dx, dy in NEIGHBORS:
                    x = dx + a
                    y = dy + b
                    if x >= 0 and x < WIDTH and y >= 0 and y < HEIGHT and breakable_map[y][x] <= repair_turn:
                        s = max(s, score_map_2[y][x])
                score_map_2[b][a] = energies[b][a] + 0.9 * s
                if base_map[b][a]:
                    score_map_2[b][a] += UNIT_COST

def set_breakable_map(my_units, enemy_units, enemy_bases):
    global breakable_map
    breakable_map = [[0 for i in range(WIDTH)] for j in range(HEIGHT)]

    for e in my_units:
        breakable_map[e.y][e.x] = GAME_LENGTH
    for e in enemy_units:
        breakable_map[e.y][e.x] = e.last_repair_turn
        for dx, dy in DIRS:
            x = e.x + dx
            y = e.y + dy
            if x > -1 and y > -1 and x < WIDTH and y < HEIGHT:
                breakable_map[y][x] = e.last_repair_turn
    for e in enemy_bases:
        breakable_map[e.y][e.x] = GAME_LENGTH

def set_unit_map(my_units):
    global unit_map
    unit_map = [[0 for i in range(WIDTH)] for j in range(HEIGHT)]
    for e in my_units:
        unit_map[e.y][e.x] = 2 if e.match_turn - e.last_repair_turn >= BREAKDOWN_TURNS - 10 else 1

def set_base_map(my_bases):
    for e in my_bases:
        base_map[e.y][e.x] = True

# Once initialized, we enter an infinite loop
base_map_set = False

TOTAL_TIME = 0.5

move_dict = dict()
while True:
    start_time = time.time()
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

    # Let your creativity go wild. Feel free to change this however you want and
    # submit it as many times as you want to the servers

    # spawn unit until we have 4 units
    set_breakable_map(my_units, enemy_units, enemy_bases)

    for unit in my_units:
        if time.time() - start_time > 0.8:
            break
        if unit.match_turn - unit.last_repair_turn > 80:
            breakable_map[unit.y][unit.x] = 0
            set_score_map_2(unit, TOTAL_TIME / len(my_units))
            move = [0, 0]
            score = score_map_2[unit.y][unit.x]
            for dx, dy in NEIGHBORS:
                x = unit.x + dx
                y = unit.y + dy
                if x >= 0 and x < WIDTH and y >= 0 and y < HEIGHT:
                    s = score_map_2[y][x]
                    if breakable_map[y][x] > unit.last_repair_turn:
                        s -= UNIT_COST
                    if s > score:
                        score = s
                        move = [dx, dy]
            dir = move_to_dir(move)
            if dir is not None:
                commands.append(unit.move(move_to_dir(move)))
            breakable_map[unit.y][unit.x] = GAME_LENGTH
        else:
            breakable_map[unit.y][unit.x] = 0
            set_score_map(unit, TOTAL_TIME / len(my_units))
            move = [0, 0]
            score = score_map[unit.y][unit.x]
            for dx, dy in NEIGHBORS:
                x = unit.x + dx
                y = unit.y + dy
                if x >= 0 and x < WIDTH and y >= 0 and y < HEIGHT:
                    s = score_map[y][x]
                    if breakable_map[y][x] > unit.last_repair_turn:
                        s -= UNIT_COST
                    if s > score:
                        score = s
                        move = [dx, dy]
            dir = move_to_dir(move)
            if dir is not None:
                commands.append(unit.move(move_to_dir(move)))
            breakable_map[unit.y][unit.x] = GAME_LENGTH

    set_unit_map(my_units)
    if time.time() - start_time < 0.8:
        set_score_map(max_time=0.1)
    for base in sorted(my_bases, key=lambda base: score_map[base.pos.y][base.pos.x], reverse=True):
        if not player.energium >= UNIT_COST:
            break
        if unit_map[base.pos.y][base.pos.x]:
            continue
        if score_map[base.pos.y][base.pos.x] * (GAME_LENGTH - agent.turn - 1) < UNIT_COST:
            continue
        for dx, dy in DIRS:
            x = base.pos.x + dx
            y = base.pos.y + dy
            if unit_map[y][x] == 2:
                break
        else:
            commands.append(base.spawn_unit())
            player.energium -= UNIT_COST

    ### AI Code ends here ###

    # submit commands to the engine
    print(','.join(commands))

    # now we end our turn
    agent.end_turn()
