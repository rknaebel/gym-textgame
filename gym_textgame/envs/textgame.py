#
#
#
import sys
import random
import os, subprocess, time, signal, sys
import csv

import gym
from gym import error, spaces
from gym import utils
from gym.utils import seeding

"""

"""
class HomeWorld(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        # we have a two dimensional discrete action space: action x object
        self.action_space = None
        self.status = ""
        self.last_action = None
        self.last_state = None
        self.last_reward = None
        self.last_terminal = None
        self.vocab = []
        self.rng = random.Random()
        self.logger_file = None
        self.log_writer = None
        self.step_log = 0
        self.mode = 0
        self.ep_log = 0
        self.epoch_log = 0
        self.hints_log = [0, 0, 0] # sleepy, bored, hungry
        self.quest_log = 0
    
    def set_mode(self, mode):
        if mode == "train":
            self.mode = 0
        self.mode = 1
    
    def log_nextEpoch(self):
        self.epoch_log += 1
        self.ep_log = 0
    
    def log(self, row):
        if not self.logger_file or not self.log_writer:
            self.logger_file = open('game_logs{}.csv'.format(self.mode), 'wb')
            self.log_writer = csv.writer(self.logger_file, delimiter=",", quotechar="'", quoting=csv.QUOTE_MINIMAL)
        self.log_writer.writerow(row)

    def set_seed(self, seed):
        self.rng = random.Random(seed)

    def get_vocab_size(self):
        return len(self.vocab)

    def permutation(self,xs):
        lst = xs[:]
        self.rng.shuffle(lst)
        return lst

    def _step(self, action):
        action = self.get_action(action)
        state, reward = self.do(action)
        terminal = self.is_terminal()
        
        #self.log([action, state])
        self.step_log += 1

        self.last_action = action
        self.last_state = state
        self.last_reward = reward
        self.last_terminal = terminal

        return state, reward, terminal, {}

    def _reset(self):
        self.log([self.mode, self.epoch_log, self.ep_log, self.step_log, self.last_action, self.last_state, self.last_reward, self.last_terminal, self.hints_log, self.quest_log])
        self.step_log = 0
        self.ep_log += 1
        self.hints_log = [0, 0, 0] # sleepy, bored, hungry
        self.quest_log = 0
        ##################
        state = self.reset_env()
        self.last_state = state
        self.last_action = None
        self.last_reward = None
        self.last_terminal = None
        return state

    def _seed(self, seed=None):
        if seed:
            self.set_seed(seed)
            return [seed]
        return []

    def _render(self, mode="human", close=False):
        #outfile = StringIO() if mode == 'ansi' else sys.stdout
        outfile = sys.stdout
        if self.last_action: outfile.write("> {}\n".format(self.last_action))
        outfile.write("{}\n".format(self.last_state))
        time.sleep(0.5)
        return outfile
