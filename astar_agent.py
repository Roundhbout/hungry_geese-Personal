
from kaggle_environments.envs.hungry_geese.hungry_geese import Observation, Configuration, Action, row_col, translate, adjacent_positions, min_distance
from random import choice

# manhattan distance for two coordinates
def manhattan_distance(x1, x2, y1, y2):
    return abs(x1 - x2) + abs(y1 - y2)

def get_valid_successors(player_head, cols, rows, bad_positions):
    valid_successors = []
    for action in Action:
        neighbor = translate(player_head, action, cols, rows)
        if neighbor not in bad_positions:
            valid_successors.append(neighbor)
    return valid_successors


def astar(curr_pos, cols, rows, bad_positions, goal):
    cur_row, cur_col = row_col(curr_pos, cols)
    goal_row, goal_col = row_col(goal, cols)
    frontier = [(curr_pos, 0, manhattan_distance(cur_row, goal_row, cur_col, goal_col))]
    explored = []
    while True:
        if len(frontier) == 0:
            return None
        frontier.sort(key=lambda x: x[1])
        curr = frontier.pop(0)
        curr_pos, curr_step, curr_prio = curr
        explored.append(curr_pos)
        if curr_pos == goal:
            return curr_prio
        for next_pos in get_valid_successors(curr_pos, cols, rows, bad_positions):
            next_row, next_col = row_col(next_pos, cols)
            next_step = curr_step + 1
            next_prio = next_step + manhattan_distance(next_row, goal_row, next_col, goal_col)
            next_node = (next_pos, next_step, next_prio)
            if next_pos not in explored:
                frontier_states = [node[0] for node in frontier]
                if next_pos not in frontier_states:
                    frontier.append(next_node)
                
                elif next_pos in frontier_states and next_prio < [prio for pos, step, prio in frontier if next_pos == pos][0]:
                    frontier.remove((next_pos, [step for pos, step, prio in frontier if next_pos == pos][0], [prio for pos, step, prio in frontier if next_pos == pos][0]))
                    frontier.append(next_node)
    
def min_astar_distance(pos, cols, rows, bad_positions, food):
    best_distance = None
    for nom in food:
        cur_distance = astar(pos, cols, rows, bad_positions, nom)
        if cur_distance == None:
            return None
        elif best_distance is None or cur_distance < best_distance:
            best_distance = cur_distance
    return best_distance



def get_bad_positions(all_geese, enemy_geese, board_cols, board_rows, food):
    bad_positions = []

    # don't move into any goose body (including our own)
    for goose in all_geese:
        for pos in goose:
            bad_positions.append(pos)
    
    # don't move next to the enemy goose head (we can get cut off)
    for enemy in enemy_geese:
        enemy_head = enemy[0]
        is_next_to_food = False
        for pos in adjacent_positions(enemy_head, board_cols, board_rows):
            if pos in food:
                is_next_to_food = True
            bad_positions.append(pos)
        # if the opponent is about to get food, their tail is about to grow
        if is_next_to_food:
            bad_positions.append(enemy[-1])
    
    return bad_positions


last_action = None

"""
This is a greedy searching agent using a manhattan distance heuristic. It checks for collision.
"""
def agent(observation, configuration):

    global last_action

    # get the observation and config of the game
    obs = Observation(observation)
    config = Configuration(configuration)

    board_rows, board_cols = config.rows, config.columns
    # get our agent's index
    player_index = obs.index

    #all geese in the game
    all_geese = obs.geese

    # this is our goose, a list of coordinates afaik
    player_goose = all_geese[player_index]
    
    # these are the enemy geese, a list of lists of coordinates
    enemy_geese = [goose for idx, goose in enumerate(all_geese) if idx != player_index and len(goose) > 0]

    # this is the position of our goose's head. movement should be based off here
    player_head = player_goose[0]

    # list of coordinates of food
    food = obs.food

    # get positions we don't want to be in
    bad_positions = get_bad_positions(all_geese, enemy_geese, board_cols, board_rows, food)
    
    # this will become a dict of all actions and their cost to the nearest food
    action_distances = {}
    not_bad_actions = []

    for action in Action:
        if last_action is None or action.opposite() != last_action:
            neighbor = translate(player_head, action, board_cols, board_rows)

            if neighbor not in bad_positions:
                not_bad_actions.append(action)
                dist = min_astar_distance(neighbor, board_cols, board_rows, bad_positions, food)
                if dist is not None:
                    action_distances[action] = dist
    
    # if there are actions here, choose the one with the smallest manhattan distance
    if len(action_distances) > 0:
        best_action = min(action_distances, key=action_distances.get)
        last_action = best_action
        return best_action.name

    # we have to move regardless
    else:
        if len(not_bad_actions) > 0:
            usable_actions = not_bad_actions
        else:
            usable_actions = Action
        if last_action is not None:
            next_action = choice([action for action in usable_actions if action != last_action.opposite()])
        else:
            next_action = choice([action for action in usable_actions])
        last_action = next_action
        return next_action.name
