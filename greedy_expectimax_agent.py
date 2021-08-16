from kaggle_environments.envs.hungry_geese.hungry_geese import Observation, Configuration, Action, row_col, translate, adjacent_positions, min_distance
from random import choice

# manhattan distance for two coordinates
def manhattan_distance(x1, x2, y1, y2):
    return abs(x1 - x2) + abs(y1 - y2)


# return a list of food that we are closest to among all enemies
def find_feasible_food(player_head, enemy_heads, food, columns):
    p_row, p_col = row_col(player_head, columns)

    feasible_food = []
    for nom in food:
        is_feasible = True
        nom_row, nom_col = row_col(nom, columns)
        for e_head in enemy_heads:
            e_row, e_col = row_col(e_head, columns)
            if manhattan_distance(p_row, nom_row, p_col, nom_col) > manhattan_distance(e_row, nom_row, e_col, nom_col):
                is_feasible = False
        if is_feasible:
            feasible_food.append(nom)
    
    return feasible_food


last_action = None
"""
This is a greedy searching agent using ucs. It checks for collision.
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

    # row column coordinates of our current head
    player_row, player_column = row_col(player_head, config.columns)

    # list of coordinates of food
    food = obs.food

    feasible_food = find_feasible_food(player_head, [g[0] for g in enemy_geese], food, board_cols)
    # get positions we don't want to be in
    bad_positions = []

    # also want to keep track of enemy head next steps for later
    """
    4/14 Currently not sure how to do this, but i want to turn away my agent from going to food if someone else is going to beat my agent to it. I can check for this, but      i don't know how to have this reevaluate which feasible food is the closest. Might have to write a big function to do this.
    """
    enemy_head_neighbors = []

    # don't move into any goose body (including our own)
    for goose in all_geese:
        for pos in goose:
            bad_positions.append(pos)
    
    # don't move next to the enemy goose head (we can get cut off)
    """
    4/14 this currently results in geese killing themselves when they end up not having to.
    I'd have to check if the enemy goose actually wants to cut us off or if it's just cruising by (this won't be easy to check).
    """
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
                if feasible_food:
                    action_distances[action] = min_distance(neighbor, feasible_food, board_cols)
    
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
