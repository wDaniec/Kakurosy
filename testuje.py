import random
from pulp import *
import json
import copy
import sys

DEBUG = False

FILENAME = "puzzles{}_{}.txt".format(sys.argv[1], sys.argv[2])
OUT_FILENAME = "ready_{}_{}.txt".format(sys.argv[1], sys.argv[2])
if DEBUG:
    FILENAME = "in_stupid_cases.txt"
    OUT_FILENAME = "out_stupid_cases"
print FILENAME
def solve(data_fills, data_totals):
        data_filled = []
        # Remember to zero down the indices
        vals = [str(i) for i in range(1, 10)]
        cols = [str(i) for i in range(1, 11)]
        rows = [str(i) for i in range(1, 19)]
        prob = LpProblem("Kakuro Problem", LpMinimize)
        choices = LpVariable.dicts("Choice", (vals, rows, cols), 0, 1, LpInteger)
        # The complete set of boolean choices
        prob += 0, "Arbitrary Objective Function"
        # Force singular values. Even for extraneous ones
        for r in rows:
            for c in cols:
                prob += lpSum([choices[v][r][c] for v in vals]) == 1, ""

        # Force uniqueness in each 'zone' and sum constraint for that zone
        # Row zones
        for r in rows:
            zonecolsholder = []
            activated = False
            zonecolssumholder = 0
            for c in cols:
                if not activated and [int(r)-1,int(c)-1] in data_fills:
                    activated = True
                    zonecolsholder = zonecolsholder +[c]
                    zonecolssumholder = [elem[0] for elem in data_totals if elem[1]=='h' and elem[2] == int(r)-1 and elem[3] == int(c)-2][0]
                    if c == "10":
                        # Uniqueness in that zone of columns
                        for v in vals:
                            prob += lpSum([choices[v][r][co] for co in zonecolsholder]) <= 1, ""
                        # Sum constraint for that zone of columns
                        prob += lpSum([int(v) * choices[v][r][co] for v in vals for co in zonecolsholder]) == zonecolssumholder, ""
                elif activated and [int(r)-1,int(c)-1] in data_fills:
                    zonecolsholder = zonecolsholder + [c]
                    if c == "10":
                        # Uniqueness in that zone of columns
                        for v in vals:
                            prob += lpSum([choices[v][r][co] for co in zonecolsholder]) <= 1, ""
                        # Sum constraint for that zone of columns
                        prob += lpSum([int(v) * choices[v][r][co] for v in vals for co in zonecolsholder]) == zonecolssumholder, ""
                elif activated and [int(r)-1,int(c)-1] not in data_fills:
                    activated = False
                    # Uniqueness in that zone of columns
                    for v in vals:
                        prob += lpSum([choices[v][r][co] for co in zonecolsholder]) <= 1, ""
                    # Sum constraint for that zone of columns
                    prob += lpSum([int(v)*choices[v][r][co] for v in vals for co in zonecolsholder]) == zonecolssumholder, ""
                    zonecolssumholder = 0
                    zonecolsholder = []

        # Col zones
        for c in cols:
            zonerowsholder = []
            activated = False
            zonerowssumholder = 0
            for r in rows:
                if not activated and [int(r)-1,int(c)-1] in data_fills:
                    activated = True
                    zonerowsholder = zonerowsholder +[r]
                    zonerowssumholder = [elem[0] for elem in data_totals if elem[1]=='v' and elem[2] == int(r)-2 and elem[3] == int(c)-1][0]
                    if r == "18":
                        # Uniqueness in that zone of rows
                        for v in vals:
                            prob += lpSum([choices[v][ro][c] for ro in zonerowsholder]) <= 1, ""
                        # Sum constraint for that zone of rows
                        prob += lpSum([int(v) * choices[v][ro][c] for v in vals for ro in zonerowsholder]) == zonerowssumholder, ""
                elif activated and [int(r)-1,int(c)-1] in data_fills:
                    zonerowsholder = zonerowsholder + [r]
                    if r == "18":
                        # Uniqueness in that zone of rows
                        for v in vals:
                            prob += lpSum([choices[v][ro][c] for ro in zonerowsholder]) <= 1, ""
                        # Sum constraint for that zone of rows
                        prob += lpSum([int(v) * choices[v][ro][c] for v in vals for ro in zonerowsholder]) == zonerowssumholder, ""
                elif activated and [int(r)-1,int(c)-1] not in data_fills:
                    activated = False
                    # Uniqueness in that zone of rows
                    for v in vals:
                        prob += lpSum([choices[v][ro][c] for ro in zonerowsholder]) <= 1, ""
                    # Sum constraint for that zone of rows
                    prob += lpSum([int(v)*choices[v][ro][c] for v in vals for ro in zonerowsholder]) == zonerowssumholder, ""
                    zonerowssumholder = 0
                    zonerowsholder = []

        # Force all extraneous values to 1 (arbitrary) | Possibly many times
        for ite in data_totals:
            prob += choices["1"][str(ite[2]+1)][str(ite[3]+1)] == 1, ""
        # Suppress calculation messages
        GLPK(msg=0).solve(prob)
        # Solution: The commented print statements are for debugging aid.
        for v in prob.variables():
            # print v.name, "=", v.varValue
            sol_arr = v.name.split('_')
            if v.varValue == 1 and [int(sol_arr[2])-1, int(sol_arr[3])-1] in data_fills:
            #     # print v.name, ":::", v.varValue, [int(v.name[9])-1, int(v.name[11])-1, int(v.name[7])]
                data_filled = data_filled + [[int(sol_arr[2])-1, int(sol_arr[3])-1, int(sol_arr[1])]]
        
        # print(data_filled)
        return data_filled


################################################   Ta czesc moze nie dzialac dobrze   ###############################################
# tutaj te wariaty sa pozmieniane, bo ktos gupio napisal kod
# ogolnie to jest [down, right] - takie jest priority na polozeniach

def check_horizontal(id_x, id_y, data_fills):
    edges = []
    idc_y = id_y+1
    while([id_x, idc_y] in data_fills):
        edges.append([[id_x, id_y], [id_x, idc_y]])
        idc_y += 1

    idc_y = id_y-1
    while([id_x, idc_y] in data_fills):
        edges.append([[id_x, id_y], [id_x, idc_y]])
        idc_y -= 1
    
    return edges

def check_horizontal_right(id_x, id_y, data_fills):
    edges = []
    idc_y = id_y+1
    while([id_x, idc_y] in data_fills):
        edges.append([[id_x, id_y], [id_x, idc_y]])
        idc_y += 1
    
    return edges

def check_vertical(id_x, id_y, data_fills):
    edges = []
    idc_x = id_x+1
    while([idc_x, id_y] in data_fills):
        edges.append([[id_x, id_y], [idc_x, id_y]])
        idc_x += 1

    idc_x = id_x-1
    while([idc_x, id_y] in data_fills):
        edges.append([[id_x, id_y], [idc_x, id_y]])
        idc_x -= 1
    
    if not edges:
        print("wtf?")
    return edges

def check_vertical_down(id_x, id_y, data_fills, new_position=[None, None]):
    id_new_x, id_new_y = new_position
    edges = []
    idc_x = id_x+1
    while([idc_x, id_y] in data_fills):
        if id_new_x == None:
            edges.append([[id_x, id_y], [idc_x, id_y]])
        else:
            edges.append([[id_new_x, id_new_y], [idc_x, id_y]])
        idc_x += 1

    return edges

def mix_empty(data_fills):
    edges = []
    for empty_field in data_fills:
        id_x, id_y = empty_field

        edges += check_vertical(id_x, id_y, data_fills)
        edges += check_horizontal(id_x, id_y, data_fills)

    return edges



def mix_values(data_totals, data_fills):
    starting_x = 0
    temp = copy.copy(data_fills)
    temp += [[x[2], x[3]] for x in data_totals]
    temp2 = [[x[1], x[2], x[3]] for x in data_totals]

    edges = []

    for idc, filled_field in enumerate(data_totals):
        _, direction, id_x, id_y = filled_field
        if direction == 'h':
            edges += check_horizontal_right(id_x, id_y, data_fills)
        elif direction == 'v':
            if ['h', id_x, id_y] in temp2:
                while [0, starting_x] in temp:
                    starting_x += 1
                data_totals[idc] = [filled_field[0], filled_field[1], 0, starting_x]
                edges += check_vertical_down(id_x, id_y, data_fills, [0, starting_x])
                temp.append([0, starting_x])
            edges += check_vertical_down(id_x, id_y, data_fills)

    return edges

def map_to_1d(data_totals, data_fills, solution, edges):
    good_edges = []
    good_nodes = []
    good_solution = []

    temp = [[x[0], x[1], 0] for x in data_fills]
    temp += [[x[2], x[3], x[0]] for x in data_totals]
    temp.sort() # w zasadzie to nie musze sortowac

    mapping = {(temp[i][0], temp[i][1]): i for i in range(len(temp))}
    for idc, (node_in, node_out) in enumerate(edges):
        new_id_in = mapping[tuple(node_in)]
        new_id_out = mapping[tuple(node_out)]
        good_edges.append((new_id_in, new_id_out))
    
    for idc, node in enumerate(temp):
        new_id = mapping[(node[0], node[1])]
        good_nodes.append((new_id, node[2]))
    
    for idc, node in enumerate(solution):
        new_id = mapping[(node[0], node[1])]
        good_solution.append([new_id, node[2]])
    
    # add to solution nodes saying only the needed values
    for node in temp:
        if [node[0], node[1]] not in data_fills:
            new_id = mapping[(node[0], node[1])]
            good_solution.append([new_id, 0])
    
    solved_ids = [node[0] for node in good_solution]
    max_solved_ids = max(solved_ids)

    good_solution.sort()
    
    return [good_nodes, good_solution, good_edges]

##################################################################################################################

def load_another():
    print(FILENAME)
    print(OUT_FILENAME)
    data_filled = []
    data_fills = []
    data_totals = []
    edges = []
    puzzlebank = []
    try:
        file = open(FILENAME, "r")
    except IOError:
        print "Could not acquire read access to file: {}".format(FILENAME)
        sys.exit()
    with file:
        for line in file:
            if line.rstrip("\r\n").isdigit():
                puzzlebank = puzzlebank + [int(line)]
        file.close()
    puzzlebank = [ele for ele in puzzlebank]
    numpuzzles = len(puzzlebank)
    print(numpuzzles)
    if len(puzzlebank) == 0:
        print "Uh-Oh! You have exhausted the puzzle bank! Gather more puzzles!"
        sys.exit()
    print "There seem to be " + str(numpuzzles) + " unique (untried in this session) puzzles!"
    print "Randomly picking one..."

    # ctr = 0
    # currprob = 1.0 / (numpuzzles - ctr)
    # currguess = random.random()
    # while (currguess > currprob and ctr < numpuzzles - 1):
    #     ctr = ctr + 1
    #     currprob = 1.0 / (numpuzzles - ctr)
    #     currguess = random.random()
    # gameId = puzzlebank[ctr]
    # print ctr
    # print "Selected puzzle: Number " + str(puzzlebank[ctr]) + ". Click anywhere on the grid to begin..."
    counter = 0
    with open(FILENAME, "r") as file:
        with open(OUT_FILENAME, 'a') as filehandle:
            readstatus = 0
            for idx, line in enumerate(file):
                line = line.strip('\n').split('_')
                # len(line) == 1 means that it's a number
                # len(line) == 4 means it's a contraint-square
                # len(line) == 3 means it's a fillable-square
                if readstatus == 0 and len(line) == 1:
                    readstatus = 1
                    continue
                if readstatus == 1 and len(line) == 1:
                    counter += 1
                    if(counter < 620):
                        print(counter, ': ignoring')
                        continue
                    print(counter)
                    solution = solve(data_fills, data_totals)
                    edges += mix_empty(data_fills)
                    edges += mix_values(data_totals, data_fills)
                    instance = map_to_1d(data_totals, data_fills, solution, edges)
                    json.dump(instance, filehandle)
                    filehandle.write('\n')
                    data_fills = []
                    data_totals = []
                    edges = []
                elif readstatus == 1:
                    if len(line) == 3:
                        data_fills = data_fills + [[int(line[1]), int(line[2])]]
                    else:
                        data_totals = data_totals + [[int(line[0]), line[1], int(line[2]), int(line[3])]]


grids = ["9x17"]
levels = ["easy", "intermediate", "hard", "challenging", "expert"]

# for grid in grids:
#     for hardness in levels:
#         FILENAME = "puzzles{}_{}.txt".format(grid, hardness)
#         OUT_FILENAME = "ready_{}_{}.txt".format(grid, hardness)
load_another()




# read_dataset()
