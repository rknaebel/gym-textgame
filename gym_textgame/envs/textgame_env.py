import os, subprocess, time, signal, sys
import random
#random.seed(42)

import gym
import gym_textgame

from gym import error, spaces
from gym import utils
from gym.utils import seeding


#import logging
#logger = logging.getLogger(__name__)

#      ------------          ----------
#      |living    |          |garden  |
#Limbo-+   00     +----------+  01    |
#      |          |          |        |
#      -----+------          ----+-----
#           |                    |
#      -----+------          ----+-----
#      |bedroom   |          |kitchen |
#      |   03     +----------+  02    |
#      |          |          |        |
#      ------------          ----------

class HomeWorld(object):
    def __init__(self):
        self.rng = random.Random()
        #
        # environment definition
        #
        self.descriptions = {
            "Living" : ["This room has a couch, chairs and TV.",
                        "You have entered the living room. You can watch TV here.",
                        "This room has two sofas, chairs and a chandelier."],
            "Garden" : ["This space has a swing, flowers and trees.",
                        "You have arrived at the garden. You can exercise here.",
                        "This area has plants, grass and rabbits."],
            "Kitchen" : ["This room has a fridge, oven, and a sink.",
                         "You have arrived in the kitchen. You can find food and drinks here.",
                         "This living area has pizza, coke, and icecream."],
            "Bedroom" : ["This area has a bed, desk and a dresser.",
                         "You have arrived in the bedroom. You can rest here.",
                         "You see a wooden cot and a mattress on top of it."]
        }
        self.env_objects = {
            "tv" : ("Living", "watch", "A huge television that is great for watching games."),
            "bike" : ("Garden", "exercise", "A nice shiny bike that is fun to ride."),
            "apple" : ("Kitchen", "eat", "A red juicy fruit."),
            "bed" : ("Bedroom", "sleep", "A nice, comfortable bed with pillows and sheets.")
        }
        self.moves = {
            'north': [("Bedroom","Living"), ("Kitchen","Garden")],
            'south': [("Living","Bedroom"), ("Garden","Kitchen")],
            'east':  [("Living","Garden"),("Bedroom","Kitchen")],
            'west':  [("Garden","Living"),("Kitchen","Bedroom")]
        }

        self.actions = ["eat", "sleep", "watch", "exercise", "go"]
        self.objects = self.env_objects.keys() + self.moves.keys()

        self.action_meanings = ["go " + d for d in self.moves.keys()] + ["{} {}".format(a,o) for o,(_,a,_) in self.env_objects.items()]
        self.num_actions = len(self.actions)
        self.num_objects = len(self.objects)

        self.rooms = self.descriptions.keys()
        self.quests = ['You are hungry','You are sleepy', 'You are bored', 'You are getting fat']
        self.quests_mislead = ['You are not hungry','You are not sleepy', 'You are not bored', 'You are not getting fat']

        self.quest_actions = ['eat', 'sleep', 'watch' ,'exercise']
        #self.quest_checklist = []
        #self.mislead_quest_checklist = []

        self.extra_vocab = ['nothing', 'happend', 'not', 'but', 'now']

        self.state = None

        self.init_vocab()
        # reset and initialize environment

    def set_seed(self, seed):
        self.rng = random.Random(seed)

    def init_vocab(self):
        words = ([d for ds in self.descriptions.values() for d in ds] +
                 [d[2] for d in self.env_objects.values()] +
                 self.rooms +
                 self.action_meanings +
                 self.quests +
                 self.extra_vocab)
        self.vocab = reduce(lambda x,y: x | y, (set(d.split()) for d in words))

    def get_vocab_size(self):
        return len(self.vocab)


    def get_quest(self):
        _, _, q_i, qm_i = self.state
        if q_i == -1: return "There is nothing to do."
        if qm_i >= 0:
            return "{} now but {} now.".format(self.quests_mislead[qm_i], self.quests[q_i])
        return "{} now.".format(self.quests[q_i])

    def get_room_desc(self):
        loc, loc_desc, _, _ = self.state
        room = self.rooms[loc]
        return self.descriptions[room][loc_desc]

    def get_output(self):
        return self.get_room_desc() + " " + self.get_quest()

    def get_location(self):
        return self.rooms[self.state[0]]

    def get_action(self,action):
        return self.actions[action[0]] + " " + self.objects[action[1]]

    def is_executable(self, action, obj):
        loc = self.get_location()
        if action == "go":
            if obj not in self.moves: return False
            return loc in [r1 for r1,r2 in self.moves[obj]]
        elif action in self.quest_actions:
            if obj not in self.env_objects: return False
            l, a, _ = self.env_objects[obj]
            return (loc == l) and (action == a)
        else:
            return False

    def is_terminal(self):
        return self.state[2] == -1

    def do(self, action, obj):
        """
        Action execution function: return next state and reward for executing action
        in current state
        """
        # check whether action does change the state - executability
        if self.is_executable(action, obj):
            if action == "go":
                for (from_loc,to_loc) in self.moves[obj]:
                    if self.get_location() == from_loc:
                        self.state[0] = self.rooms.index(to_loc)
                        self.state[1] = self.rng.randint(0,2)
                        return self.get_output(), -0.01
            else:
                obj_desc = self.env_objects[obj][2]
                r = 1 if self.quest_actions.index(action) == self.state[2] else -0.01
                if r == 1: self.state[2] = -1
                return obj_desc, r
        # if not, return "Nothing happend." and same state description
        else:
            return "Nothing happend. " + self.get_output(), -0.1

    def reset(self):
        location = self.rng.randint(0,len(self.rooms)-1)
        location_desc = self.rng.randint(0,2)
        quest = self.rng.randint(0,len(self.quests)-1)
        quest_mislead = self.rng.randint(0,len(self.quests)-1)
        if quest_mislead == quest: quest_mislead = -1

        self.state = [location, location_desc, quest, quest_mislead]
        return self.get_output()


class HomeWorldEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        #
        # Home world
        #
        self.env = HomeWorld()

        # set the observation space to the vocab size and some kind of sequencial
        # data
        self.observation_space = None
        self.vocab_space = self.env.get_vocab_size()
        self.seq_length = 100
        # we have a two dimensional discrete action space: action x object
        self.action_space = spaces.Tuple((spaces.Discrete(self.env.num_actions), spaces.Discrete(self.env.num_objects)))
        self.status = ""
        self.last_action = None
        self.last_state = None

    def get_action_meanings(self):
        return self.env.action_meanings

    def _step(self, action):
        act,obj = self.env.actions[action[0]], self.env.objects[action[1]]
        state, reward = self.env.do(act,obj)
        terminal = self.env.is_terminal()

        self.last_action = act + " " + obj
        self.last_state = state

        return state, reward, terminal, {}

    def _reset(self):
        state = self.env.reset()
        self.last_state = state
        self.last_action = None
        return state

    def _seed(self, seed=None):
        if seed:
            self.env.set_seed(seed)
            return [seed]
        return []

    def _render(self, mode="human", close=False):
        #outfile = StringIO() if mode == 'ansi' else sys.stdout
        outfile = sys.stdout
        if self.last_action: outfile.write("> {}\n".format(self.last_action))
        outfile.write("{}\n".format(self.last_state))
        time.sleep(0.5)
        return outfile

if __name__ == "__main__":
    env = gym.make("HomeWorld-v0")
    done = False

    s = env.reset()
    print s
    while not done:
        a = env.action_space.sample()
        s, r, done, info = env.step(a)
        print a, s
    print "done!"
