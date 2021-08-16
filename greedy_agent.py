from kaggle_environments.envs.hungry_geese.hungry_geese import Observation, Configuration, Action, row_col, translate, adjacent_positions, min_distance
from random import choice

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
    
    player_index = obs.index

    all_geese = obs.geese

    player_goose = all_geese[player_index]
    
    enemy_geese = [goose for idx, goose in enumerate(all_geese) if idx != player_index and len(goose) > 0]

    player_head = player_goose[0]

    food = obs.food

    # get positions we don't want to be in
    bad_positions = []

    # also want to keep track of enemy head next steps for later
    enemy_head_neighbors = []

    # don't move into any goose body (including our own)
    for goose in all_geese:
        for pos in goose:
            bad_positions.append(pos)
    
    # don't move next to the enemy goose head (we can get cut off)
    for enemy in enemy_geese:
        enemy_head = enemy[0]
        is_next_to_food = False
        for pos in adjacent_positions(enemy_head, board_cols, board_rows):
            enemy_head_neighbors.append(pos)
            if pos in food:
                is_next_to_food = True
            bad_positions.append(pos)
        # if the opponent is about to get food, their tail is about to grow
        if is_next_to_food:
            bad_positions.append(enemy[-1])
    
    # this will become a dict of all actions and their heuristic values
    action_distances = {}
    not_bad_actions = []

    for action in Action:
        if last_action is None or action.opposite() != last_action:
            neighbor = translate(player_head, action, board_cols, board_rows)

            if neighbor not in bad_positions:
                not_bad_actions.append(action)
                action_distances[action] = min_distance(neighbor, food, board_cols)
    
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
