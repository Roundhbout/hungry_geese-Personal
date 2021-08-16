
from kaggle_environments.envs.hungry_geese.hungry_geese import Observation, Configuration, Action

from random import choice

def agent(obs_dict, config_dict):
    return choice([action for action in Action]).name
