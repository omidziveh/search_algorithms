#-----------------------imports-----------------------

import math
import copy
import os
import treelib
import time

#-----------------------variables-----------------------

size = 0
goal = []
moves = {'down': [-1, 0], 'up': [1, 0], 'left': [0, 1], 'right': [0, -1]}

#-----------------------functions-----------------------

def g(node, tree): # depth of a node
    return tree.depth(node)

def h(state): # when a state end
    count = 0
    global size
    for i in range(1, size+1):
        for j in range(1, size+1):
            if state['board'][i-1][j-1] != '_':
                count += abs(math.ceil(int(state['board'][i-1][j-1]) / size) - i)
                j_count = int(state['board'][i-1][j-1]) % (size)
                if j_count == 0:
                    j_count = size
                count += abs(j_count - j)
    return count

def f(node, tree, state):
    return h(state) + g(node, tree)

def create_goal():
    num = 0
    for i in range(size):
        goal.append([])
        for _ in range(size):
            num += 1
            goal[i].append(str(num))
    goal[-1][-1] = '_'

def is_goal(state):
    if goal == state['board']:
        return True
    return False

def generate_moves(state):
    answer = {}
    for action in moves:
        next_state = copy.deepcopy(state)
        if moves[action][0]+state['empty'][0] != size and moves[action][1]+state['empty'][1] != size and \
                state['empty'][0]+moves[action][0] != -1 and moves[action][1]+state['empty'][1] != -1:

            # swap 0(empty) and another number place for updating the board
            next_state['board'][state['empty'][0]][state['empty'][1]], next_state['board'][state['empty'][0]+moves[action][0]][state['empty'][1]+moves[action][1]] = \
                next_state['board'][state['empty'][0]+moves[action][0]][state['empty'][1] +
                                                                        moves[action][1]], next_state['board'][state['empty'][0]][state['empty'][1]]

            # updating 'empty' place in state
            next_state['empty'][0] += moves[action][0]
            next_state['empty'][1] += moves[action][1]

            answer[action] = next_state
    return answer

def print_board(state, move):
    print(f'{move}:')
    for row in state['board']:
        for cell in row:
            print(cell, end=' ')
        print()
    print(f"empty cell is in {state['empty'][0]+1}, {state['empty'][1]+1}")
    print('------------')

def dfs(initial_state, tree_search=False):
    tree = treelib.Tree()
    tree.create_node('Root', 0, None, initial_state)
    last_id = 0
    visited, frontier = [], []
    chosen_leaf = tree.get_node(0)
    while len(frontier) > 0 or not last_id:
        if tree_search:
            if last_id:
                chosen_leaf = frontier.pop()
        else:
            while chosen_leaf.data in visited:
                chosen_leaf = frontier.pop()
            visited.append(chosen_leaf.data)
        next_states = generate_moves(chosen_leaf.data)
        for action in next_states:
            last_id += 1
            if last_id % 1000 == 0:
                print(f'{last_id} nodes', end='\r')
            tree.create_node(
                action, last_id, chosen_leaf.identifier, next_states[action])
            frontier.append(tree.get_node(last_id))
            if is_goal(next_states[action]):
                return tree, last_id

def dls(initial_state, depth, tree_search=False):
    tree = treelib.Tree()
    tree.create_node('Root', 0, None, initial_state)
    last_id = 0
    visited, frontier = [], []
    chosen_leaf = tree.get_node(0)
    while True:
        remaining = False
        if tree_search:
            if last_id > 0: 
                if len(frontier) == 0:
                    return False
                if tree.depth(chosen_leaf) < depth:
                    chosen_leaf = frontier.pop()
        else:
            while chosen_leaf.data in visited:
                if len(frontier) == 0:
                    return False
                if tree.depth(chosen_leaf) > depth:
                    pass
                else:
                    chosen_leaf = frontier.pop()
            visited.append(chosen_leaf.data)
        next_states = generate_moves(chosen_leaf.data)
        for action in next_states:
            last_id += 1
            tree.create_node(
                action, last_id, chosen_leaf.identifier, next_states[action])
            frontier.append(tree.get_node(last_id))
            if len(generate_moves(next_states[action])) > 1:
                remaining = True
            if is_goal(next_states[action]):
                return tree, last_id, remaining

def bfs(initial_state, tree_search=False):
    tree = treelib.Tree()
    tree.create_node('Root', 0, None, initial_state)
    last_id = 0
    visited, frontier = [], []
    chosen_leaf = tree.get_node(0)
    while len(frontier) > 0 or not last_id:
        if tree_search:
            if last_id:
                chosen_leaf = frontier.pop(0)
        else:
            while chosen_leaf.data in visited:
                chosen_leaf = frontier.pop(0)
            visited.append(chosen_leaf.data)
        next_states = generate_moves(chosen_leaf.data)
        for action in next_states:
            last_id += 1
            if last_id % 1000 == 0:
                print(f'{last_id} nodes', end='\r')
            tree.create_node(
                action, last_id, chosen_leaf.identifier, next_states[action])
            if h(next_states[action]) <= 1:
                print(next_states[action])
            frontier.append(tree.get_node(last_id))
            if is_goal(next_states[action]):
                return tree, last_id

def ids(initial_state, tree_search=False):
    depth = 0
    nodes = 0
    while True:
        search = dls(initial_state, depth, tree_search)
        print(search)
        if not search[2]:
            return False
        nodes += search[1]
        if search:
            return search[0], nodes
        depth += 1

def get_board(path):
    global size

    board = open(path, 'r').readlines()
    size = len(board)
    state = {}

    for i in range(len(board)):
        board[i].replace('\n', '')
        board[i] = board[i].split()
        for j in range(len(board[i])):
            if board[i][j] == '0' or board[i][j] == '_':
                state['empty'] = [i, j]

    state['board'] = board
    return state

def write_result(tree, nodes, start, end, path, problem, solvable=True):
    global size
    lst = []

    file = open(path, 'w')
    file.truncate()
    file.close()
    file = open(path, 'a')
    file.write(f"problem:\n")
    for row in problem['board']:
        for cell in row:
            file.write(f'{cell} ')
        file.write('\n')

    if not solvable:
        file.write('Sorry, there is no answer for this question!')
        print(f'answer is in {path} !')
        file.write(f"\n\ntime: {end-start}s\nnodes created: {nodes}")
        return 

    goal_node = tree.get_node(nodes)
    depth = tree.depth(goal_node)
    while not goal_node.is_root():
        lst.append([goal_node.data, goal_node.tag])
        goal_node = tree.parent(goal_node.identifier)
    
    lst.reverse()
    
    file.write("\nanswer:")

    for node in lst:
        file.write(f"\n\n{node[1]}:\n")
        for row in node[0]['board']:
            for cell in row:
                file.write(f"{cell} ")
            file.write('\n')
    
    file.write(f"\n\ntime: {end-start}s\nnodes created: {nodes}\nanswer depth: {depth}")
                
    file.close()
    print(f'answer is in {path} !')

def greedy(initial_state, tree_search=False):
    tree = treelib.Tree()
    last_id = 0
    tree.create_node('Root', 0, None, initial_state)
    frontier, sorted_frontier, visited = {}, [], []
    frontier[h(initial_state)] = [tree.get_node(0)]
    sorted_frontier = sorted(frontier)
    chosen_leaves = frontier[sorted_frontier[0]]
    # frontier := {1: [node_1], 2: [node_2, node_3], 3: [node_4] ... }
    # sorted_frontier := [1, 2, 3, 4, ...]
    # chosen_leaves = [node_1] -> [node_2, node_3] ...
    # visited = [node_1] -> [node_1, node_2] -> [node_1, node_2, node_3] ...
    while len(frontier) > 0:
        sorted_frontier = sorted(frontier)
        for H in sorted_frontier:
            chosen_leaves = frontier[H]
            del frontier[H]
            break
        for leaf in chosen_leaves:
            next_states = generate_moves(leaf.data)
            for action in next_states:
                last_id += 1
                if last_id % 1000 == 0:
                    print(last_id, sorted_frontier, end='\r')
                if not tree_search:
                    if not next_states[action] in visited:
                        tree.create_node(action, last_id, leaf, next_states[action])
                        try:
                            frontier[h(next_states[action])].append(tree.get_node(last_id))
                        except:
                            frontier[h(next_states[action])] = [tree.get_node(last_id)]
                        if is_goal(next_states[action]):
                            return tree, last_id
                        visited.append(next_states[action])
                else:
                    tree.create_node(action, last_id, leaf, next_states[action])
                    try:
                        frontier[h(next_states[action])].append(tree.get_node(last_id))
                    except:
                        frontier[h(next_states[action])] = [tree.get_node(last_id)]
                    if is_goal(next_states[action]):
                        return tree, last_id
    
def As(initial_state, tree_search=False):
    
    tree = treelib.Tree()
    last_id = 0
    tree.create_node('Root', 0, None, initial_state)
    frontier, sorted_frontier, visited = {}, [], []
    frontier[f(tree.get_node(0), tree, initial_state)] = [tree.get_node(0)]
    sorted_frontier = sorted(frontier)
    chosen_leaves = frontier[sorted_frontier[0]]
    # frontier := {1: [node_1], 2: [node_2, node_3], 3: [node_4] ... }
    # sorted_frontier := [1, 2, 3, 4, ...]
    # chosen_leaves = [node_1] -> [node_2, node_3] ...
    # visited = [node_1] -> [node_1, node_2] -> [node_1, node_2, node_3] ...
    while len(frontier) > 0:
        sorted_frontier = sorted(frontier)
        for F in sorted_frontier:
            chosen_leaves = frontier[F]
            del frontier[F]
            break
        for leaf in chosen_leaves:
            next_states = generate_moves(leaf.data)
            for action in next_states:
                last_id += 1
                if last_id % 1000 == 0:
                    print(last_id, sorted_frontier, end='\r')
                if not tree_search:
                    if not next_states[action] in visited:
                        tree.create_node(action, last_id, leaf, next_states[action])
                        try:
                            frontier[f(tree.get_node(last_id), tree, next_states[action])].append(tree.get_node(last_id))
                        except:
                            frontier[f(tree.get_node(last_id), tree, next_states[action])] = [tree.get_node(last_id)]
                        if is_goal(next_states[action]):
                            return tree, last_id, True
                        visited.append(next_states[action])
                else:
                    tree.create_node(action, last_id, leaf, next_states[action])
                    try:
                        frontier[f(tree.get_node(last_id), tree, next_states[action])].append(tree.get_node(last_id))
                    except:
                        frontier[f(tree.get_node(last_id), tree, next_states[action])] = [tree.get_node(last_id)]
                    if is_goal(next_states[action]):
                        return tree, last_id, True
    return tree, last_id, False

#-----------------------main-----------------------

state = get_board('map.txt')
create_goal()

strategy = input('strategy?(dfs, bfs, ucs, greedy, A*): ')
tree_search = eval(input('tree search?(True, False): '))
# depth = input('depth: ') if strategy == 'dls' else None

print('searching...')

start = time.time()
solvable = True

if strategy == 'dfs':
    tree, nodes = dfs(state, tree_search)
if strategy == 'bfs':
    tree, nodes = bfs(state, tree_search)

# -- still not working --     

# if strategy == 'dls':
#     tree, nodes = dls(state, depth, tree_search)
# if strategy == 'ids':
#     tree, nodes = ids(state, tree_search)

# -- still not working --

if strategy == 'ucs':
    tree, nodes = bfs(state, tree_search)
if strategy == 'greedy':
    tree, nodes = greedy(state, tree_search)
if strategy == 'A*':
    tree, nodes, solvable = As(state, tree_search)

end = time.time()

if strategy == 'A*':
    strategy = 'As'

try:
    os.mkdir('res')
except:
    pass

write_result(tree, nodes, start, end, f"res/{strategy}.txt", state, solvable)
