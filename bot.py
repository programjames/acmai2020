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
energiums = [[game_map.get_tile(i, j).energium for i in range(WIDTH)] for j in range(HEIGHT)]
energies = [[energiums[j][i] for i in range(WIDTH)] for j in range(HEIGHT)]
score_map = [[energies[j][i] for i in range(WIDTH)] for j in range(HEIGHT)]
score_map_2 = [[energies[j][i] for i in range(WIDTH)] for j in range(HEIGHT)]
score_map_3 = [[energies[j][i] for i in range(WIDTH)] for j in range(HEIGHT)]
R = 0.95
r = 0
rounds_left = GAME_LENGTH
def set_score_map(max_time=0.05):
    global score_map, energies
    score_map = [[energies[j][i] for i in range(WIDTH)] for j in range(HEIGHT)]
    t = time.time()
    depth = 0
    #repair_turn = 0 if unit is None else unit.last_repair_turn
    while time.time() - t < max_time:
        depth += 1
        for a in range(WIDTH):
            for b in range(HEIGHT):
                s = energies[b][a]
                for dx, dy in NEIGHBORS:
                    x = dx + a
                    y = dy + b
                    if x >= 0 and x < WIDTH and y >= 0 and y < HEIGHT and breakable_map[y][x] < GAME_LENGTH and unit_map[y][x] == 0:
                        s = max(s, score_map[y][x])
                score_map[b][a] = r * energies[b][a] + (1-r) * R * s
def set_score_map_2(max_time=0.05):
    global score_map_2, energies
    score_map_2 = [[energies[j][i] for i in range(WIDTH)] for j in range(HEIGHT)]
    t = time.time()
    depth = 0
    while time.time() - t < max_time:
        depth += 1
        for a in range(WIDTH):
            for b in range(HEIGHT):
                s = energies[b][a]
                for dx, dy in NEIGHBORS:
                    x = dx + a
                    y = dy + b
                    if x >= 0 and x < WIDTH and y >= 0 and y < HEIGHT:
                        s = max(s, score_map_2[y][x])
                score_map_2[b][a] = r * energies[b][a] + (1-r) * R * s
                if base_map[b][a]:
                    score_map_2[b][a] += UNIT_COST
def set_score_map_3(max_time=0.05):
    global score_map_3, energies
    score_map_3 = [[energies[j][i] for i in range(WIDTH)] for j in range(HEIGHT)]
    t = time.time()
    depth = 0
    while time.time() - t < max_time:
        depth += 1
        for a in range(WIDTH):
            for b in range(HEIGHT):
                s = energies[b][a]
                for dx, dy in NEIGHBORS:
                    x = dx + a
                    y = dy + b
                    if x >= 0 and x < WIDTH and y >= 0 and y < HEIGHT:
                        s = max(s, score_map_3[y][x])
                score_map_3[b][a] = r * energies[b][a] + (1-r) * R * s

def set_breakable_map(my_units, enemy_units, enemy_bases):
    global breakable_map
    breakable_map = [[0 for i in range(WIDTH)] for j in range(HEIGHT)]
    enemies_here = [[False for i in range(WIDTH)] for j in range(HEIGHT)]

##    for e in my_units:
##        breakable_map[e.y][e.x] = GAME_LENGTH
    for e in enemy_units:
        breakable_map[e.y][e.x] = e.last_repair_turn
        enemies_here[e.y][e.x] = True
        for dx, dy in DIRS:
            x = e.x + dx
            y = e.y + dy
            if x > -1 and y > -1 and x < WIDTH and y < HEIGHT and enemies_here[y][x] == False:
                breakable_map[y][x] = max(breakable_map[y][x], e.last_repair_turn)
    for e in enemy_bases:
        breakable_map[e.y][e.x] = GAME_LENGTH

def set_unit_map(my_units):
    global unit_map
    unit_map = [[0 for i in range(WIDTH)] for j in range(HEIGHT)]
    for e in my_units:
        unit_map[e.y][e.x] = 2 if need_repair[e.id] else 1

def set_base_map(my_bases):
    for e in my_bases:
        base_map[e.y][e.x] = True

# Once initialized, we enter an infinite loop
base_map_set = False

TOTAL_TIME = 0.1
MAX_TIME = 0.1

last_moves = dict()
last_scores = dict()
need_repair = dict()

while True:
    start_time = time.time()
    # wait for update from match engine
    agent.update()
    
    rounds_left = GAME_LENGTH - agent.turn
    r = 1 / (1 + 2 * rounds_left)

    commands = []

    # player is your player object, opponent is the opponent's
    player = agent.players[agent.id]
    opponent = agent.players[(agent.id + 1) % 2]
    print(agent.turn, player.energium, opponent.energium, file=sys.stderr)

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
    energies = [[energiums[j][i] for i in range(WIDTH)] for j in range(HEIGHT)]
    for unit in my_units:
        if energiums[unit.pos.y][unit.pos.x] <= 0 or unit.id not in last_moves:
            last_moves[unit.id] = "a"
        if unit.id not in need_repair or base_map[unit.pos.y][unit.pos.x]:
            need_repair[unit.id] = False
            unit.last_repair_turn = unit.match_turn
        if breakable_map[unit.pos.y][unit.pos.x] > unit.last_repair_turn or unit.match_turn - unit.last_repair_turn > 80:
            need_repair[unit.id] = True
        if last_moves[unit.id] is None:
            energies[unit.pos.y][unit.pos.x] = -UNIT_COST
        else:
            last_scores[unit.id] = score_map[unit.pos.y][unit.pos.x]
    
    set_unit_map(my_units)
    set_score_map(max_time = MAX_TIME)
    set_score_map_2(max_time = MAX_TIME)
    set_score_map_3(max_time = MAX_TIME)

    unit_map = [[0 for i in range(WIDTH)] for j in range(HEIGHT)]
    for unit in sorted(filter(lambda u: need_repair[u.id], my_units), key=lambda u: [-breakable_map[u.y][u.x], u.last_repair_turn]):
        move = [0, 0]
        score = score_map_2[unit.y][unit.x]
        if breakable_map[unit.y][unit.x] > unit.last_repair_turn or unit_map[unit.y][unit.x] > 0:
            score = -UNIT_COST
        for dx, dy in NEIGHBORS:
            x = unit.x + dx
            y = unit.y + dy
            if x >= 0 and x < WIDTH and y >= 0 and y < HEIGHT and unit_map[y][x] == 0:
                s = score_map_2[y][x]
                if breakable_map[y][x] > unit.last_repair_turn:
                    s = -UNIT_COST
                if s >= score:
                    score = s
                    move = [dx, dy]
        dir = move_to_dir(move)
        if dir is not None:
            commands.append(unit.move(move_to_dir(move)))
        unit_map[unit.y][unit.x] = 2
    
    for unit in sorted(filter(lambda u: not need_repair[u.id], my_units), key=lambda u: [-breakable_map[u.y][u.x], u.last_repair_turn]):
        move = [0, 0]
        scores = []
        score = last_scores[unit.id]
        if breakable_map[unit.y][unit.x] > unit.last_repair_turn or unit_map[unit.y][unit.x] > 0:
            score = -UNIT_COST
        scores.append(score)
        for dx, dy in NEIGHBORS:
            x = unit.x + dx
            y = unit.y + dy
            if x >= 0 and x < WIDTH and y >= 0 and y < HEIGHT and unit_map[y][x] == 0:
                #print(unit.id, x, y, unit_map[y][x], file=sys.stderr)
                s = score_map[y][x]
                if breakable_map[y][x] > unit.last_repair_turn:
                    s = -UNIT_COST
                scores.append(s)
                if s >= score:
                    score = s
                    move = [dx, dy]
        dir = move_to_dir(move)
        if dir is not None:
            commands.append(unit.move(move_to_dir(move)))
        last_moves[unit.id] = dir
        unit_map[unit.y][unit.x] = 1
    
    #print(unit_map, file=sys.stderr)

    set_unit_map(my_units)
    for base in sorted(my_bases, key=lambda base: score_map[base.pos.y][base.pos.x], reverse=True):
        if not player.energium >= UNIT_COST:
            break
        if unit_map[base.pos.y][base.pos.x]:
            continue
        if score_map_3[base.pos.y][base.pos.x] * (GAME_LENGTH - agent.turn - 1) < UNIT_COST:
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
