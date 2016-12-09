#
#
#
import random

import gym
from gym import error, spaces
from gym import utils
from gym.utils import seeding

"""

"""
class HomeWorld(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.vocab_space = self.get_vocab_size()
        # we have a two dimensional discrete action space: action x object
        self.action_space = spaces.Tuple((spaces.Discrete(self.env.num_actions), spaces.Discrete(self.env.num_objects)))
        self.status = ""
        self.last_action = None
        self.last_state = None
        self.rng = random.Random()

    def set_seed(self, seed):
        self.rng = random.Random(seed)

    def permutation(self,xs):
        lst = xs[:]
        self.rng.shuffle(lst)
        return lst

    def get_vocab_size(self):
        return len(self.vocab)

    def _step(self, action):
        action = self.get_action(action)
        state, reward = self.do(action)
        terminal = self.is_terminal()

        self.last_action = action
        self.last_state = state

        return state, reward, terminal, {}

    def _reset(self):
        state = self.reset()
        self.last_state = state
        self.last_action = None
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
