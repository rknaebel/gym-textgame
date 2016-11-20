import os, subprocess, time, signal, sys
import random
#random.seed(42)

import gym
from gym import error, spaces
from gym import utils
from gym.utils import seeding

import spacy


#import logging
#logger = logging.getLogger(__name__)

#  -----+------         ------------          ----------
#  |  hall    |         |living    |          |garden  |
#  |   05     +---------+   00     +----------+  01    |
#  |          |         |          |          |        |
#  ------------         -----+------          ----+-----
#                            |                    |
#                       -----+------          ----+-----
#                       |bedroom   |          |kitchen |
#                       |   03     +----------+  02    |
#                       |          |          |        |
#                       ------------          ----+-----
#                                                 |
#                                             ----+-----
#                                             |pantry  |
#                                             |  04    |
#                                             |        |
#                                             ----+-----

class HomeWorld2(object):
    def __init__(self):
        self.rng = random.Random()
        #
        # environment definition
        #
        self.descriptions = {
            "living" :  ["This room has a couch, chairs and TV.",
                         "You have entered the living room. You can watch TV here.",
                         "This room has two sofas, chairs and a chandelier."],
            "garden" :  ["This space has a swing, flowers and trees.",
                         "You have arrived at the garden. You can exercise here.",
                         "This area has plants, grass and rabbits."],
            "kitchen" : ["This room has a fridge, oven, and a sink.",
                         "You have arrived in the kitchen. You can find food and drinks here.",
                         "This living area has pizza, coke, and icecream."],
            "bedroom" : ["This area has a bed, desk and a dresser.",
                         "You have arrived in the bedroom. You can rest here.",
                         "You see a wooden cot and a mattress on top of it."],
            "pantry" :  ["A small room for storing food and other kinds of goods.",
                         "This area is usually used for preparing cold foods.",
                        ],
            "hall" :    ["This seems to be the entrance room of the house.",
                        ],
        }

        self.rooms = self.descriptions.keys()

        self.env_objects = {
            "tv" : "A huge television that is great for watching games.",
#            "bike" : "A nice shiny bike that is fun to ride.",
            "apple" : "A red juicy fruit.",
            "cheese" : "A good old emmentaler.",
            "pizza" : "A delicious pizza margherita.",
#            "bed" : "A nice, comfortable bed with pillows and sheets.",
            "rbutton" : "A red button.",
            "gbutton" : "A green button.",
            "bbutton" : "A blue button.",
            "ingredient1" : "A red fluid",
            "ingredient2" : "A green fluid",
            "ingredient3" : "A blue fluid",
            "recipe_book" : "",
#            "key" : "A little key to open the locked room.",
#            "door" : "Looks like the door to another room.",
        }

        self.definitions = {
            ("eat apple") :  [{
                "conds" :{"room":"kitchen", "quest":"hungry", "poisoned":"apple"},
                "effs"  :{"dead":True}
                },{
                "conds" :{"room":"kitchen", "quest":"hungry","old":"apple"},
                "effs"  :{"info":"old_food"}
                },{
                "conds" :{"room":"kitchen", "quest":"hungry"},
                "effs"  :{"quest":""}
            }],
            ("eat cheese") :  [{
                "conds" :{"room":"kitchen", "quest":"hungry", "poisoned":"cheese"},
                "effs"  :{"dead":True}
                },{
                "conds" :{"room":"kitchen", "quest":"hungry","old":"cheese"},
                "effs"  :{"info":"old_food"}
                },{
                "conds" :{"room":"kitchen", "quest":"hungry"},
                "effs"  :{"quest":""}
            }],
            ("eat pizza") :  [{
                "conds" :{"room":"kitchen", "quest":"hungry", "poisoned":"pizza"},
                "effs"  :{"dead":True}
                },{
                "conds" :{"room":"kitchen", "quest":"hungry","old":"pizza"},
                "effs"  :{"info":"old_food"}
                },{
                "conds" :{"room":"kitchen", "quest":"hungry"},
                "effs"  :{"quest":""}
            }],
            ("watch tv") : [{
                "conds" : {"room":"living", "quest":"bored", "energy":True},
                "effs"    : {"quest":""}
                },{
                "conds" : {"room":"living", "quest":"bored", "energy":False},
                "effs"    : {"info":"energy_error"}
            }],
            ("press rbutton") : [{
                "conds" :{"room":"pantry", "energy_btn":"rbutton"},
                "effs"  :{"energy":True}
                },{
                "conds" :{"room":"pantry", "shock_btn":"rbutton"},
                "effs"  :{"dead":True}
                },{
                "conds":{"room":"pantry"},
                "effs" : {}
            }],
            ("press gbutton") : [{
                "conds" :{"room":"pantry", "energy_btn":"gbutton"},
                "effs"  :{"energy":True}
                },{
                "conds" :{"room":"pantry", "shock_btn":"gbutton"},
                "effs"  :{"dead":True}
                },{
                "conds":{"room":"pantry"},
                "effs" : {}
            }],
            ("press bbutton") : [{
                "conds" :{"room":"pantry", "energy_btn":"bbutton"},
                "effs"  :{"energy":True}
                },{
                "conds" :{"room":"pantry", "shock_btn":"bbutton"},
                "effs"  :{"quest":"", "success":False}
                },{
                "conds":{"room":"pantry"},
                "effs" : {}
            }],
            ("read recipe_book") : [{
                "conds" :{"room":"garden",},
                "effs"  :{"info":"recipe_info"}
            }],
            ("mix 12") : [{
                "conds":{"room":"bedroom", "quest":"sleepy", "recipe_good":"12"},
                "effs"  :{"quest":""}
                },{
                "conds":{"room":"bedroom", "recipe_bad":"12"},
                "effs" : {"quest":"", "dead":True}
                },{
                "conds":{"room":"bedroom"},
                "effs" : {"info":"recipe_wrong"}
            }],
            ("mix 13") : [{
                "conds":{"room":"bedroom", "quest":"sleepy", "recipe_good":"13"},
                "effs"  :{"quest":""}
                },{
                "conds":{"room":"bedroom", "recipe_bad":"13"},
                "effs" : {"quest":"", "dead":True}
                },{
                "conds":{"room":"bedroom"},
                "effs" : {"info":"recipe_wrong"}
            }],
            ("mix 23") : [{
                "conds":{"room":"bedroom", "quest":"sleepy", "recipe_good":"23"},
                "effs"  :{"quest":""}
                },{
                "conds":{"room":"bedroom", "recipe_bad":"23"},
                "effs" : {"quest":"", "dead":True}
                },{
                "conds":{"room":"bedroom"},
                "effs" : {"info":"recipe_wrong"}
            }],
            #
            # Move in direction
            #
            ("go north") : [
                {"conds":{"room":"bedroom"}, "effs":{"room":"living"}},
                {"conds":{"room":"kitchen"}, "effs":{"room":"garden"}},
                {"conds":{"room":"pantry"}, "effs":{"room":"kitchen"}},
            ],
            ("go south") : [
                {"conds":{"room":"living"}, "effs":{"room":"bedroom"}},
                {"conds":{"room":"garden"}, "effs":{"room":"kitchen"}},
                {"conds":{"room":"kitchen"}, "effs":{"room":"pantry"}},
            ],
            ("go east") : [
                {"conds":{"room":"living"}, "effs":{"room":"garden"}},
                {"conds":{"room":"bedroom"}, "effs":{"room":"kitchen"}},
                {"conds":{"room":"hall"}, "effs":{"room":"living"}},
            ],
            ("go west") : [
                {"conds":{"room":"garden"}, "effs":{"room":"living"}},
                {"conds":{"room":"kitchen"}, "effs":{"room":"bedroom"}},
                {"conds":{"room":"living"}, "effs":{"room":"hall"}},
            ],
        }

        self.text = {
            "quest" : {
                "hungry" : "You are hungry",
                "sleepy" : "You are sleepy",
                "bored"  : "You are bored",
                "fat"    : "You are getting fat",
            },
            "mislead" : {
                "hungry" : "You are not hungry",
                "sleepy" : "You are not sleepy",
                "bored"  : "You are not bored",
                "fat"    : "You are not getting fat",
            },
            "info" : {
                "energy_error" : "Seems the tv does not work because of missing energy. Press the {} in the pantry.",
                "old_food" : "The food does not seem good anymore.",
                "food_warning" : "You cannot enjoy the {} anymore, it is old! Attention: do not eat the poisend {}",
                "recipe_wrong" : "The recipe seems to have the wrong effect."
            },
            "recipies" : {
                0: "To get {0} you should mix {1} and {2}.",
                1: "Recipe for being {0}: First take {1}, then {2} and at the end mix both ingredients.",
                2: "Take both, {1} and {2}, to get {0}.",
            }
        }

        self.actions = list({a.split(" ")[0] for a in self.definitions})
        self.objects = list({a.split(" ")[1] for a in self.definitions})

        self.num_actions = len(self.actions)
        self.num_objects = len(self.objects)

        self.quests = ['hungry','sleepy', 'bored']
        self.quest_actions = ['eat', 'sleep', 'watch']
        self.extra_vocab = ['nothing', 'happend', 'not', 'but', 'now']

        self.state = {
            "room" : "",
            "description" : "",
            "info" : "",
            "quest" : "",
            "mislead" : "",
            "success":True,
            "old" : "",
            "poisoned" : "",
            "energy" : "",
            "shock_btn" : "",
            "energy_btn" : "",
            "recipe_good" : "",
            "recipe_bad" : "",
            "dead" : False
        }

        self.init_vocab()
        # reset and initialize environment

    def set_seed(self, seed):
        self.rng = random.Random(seed)

    def permutation(self,xs):
        lst = xs[:]
        self.rng.shuffle(lst)
        return lst

    def init_vocab(self):
        words = u" ".join(  [d for ds in self.descriptions.values() for d in ds] +
                            self.env_objects.values() +
                            [t for k,v in self.text.iteritems() for t in v.values()] +
                            self.extra_vocab
        )
        nlp = spacy.load("en")
        d = nlp(words)
        self.vocab = set(map(lambda x: x.text, d))

    def get_vocab_size(self):
        return len(self.vocab)

    def get_quest(self):
        if not self.state["quest"]:
            return "There is nothing to do."
        if self.state["mislead"]:
            return "{} now but {} now.".format(
                self.text["mislead"][self.state["mislead"]],
                self.text["quest"][self.state["quest"]])
        return "{} now.".format(self.text["quest"][self.state["quest"]])

    def get_room_desc(self):
        return self.state["description"]

    def get_output(self):
        # generate info message
        info = ""
        if self.state["info"] == "recipe_info":
            msgs = self.permutation(self.text["recipies"].values())
            results = self.permutation(self.state["recipies"].items())
            for s,i in zip(self.permutation(self.text["recipies"].values()),self.state["recipies"].items()):
                info += s.format(i[0],i[1][0],i[1][1])
        elif self.state["info"] == "energy_error":
            info = self.text["info"]["energy_error"].format(self.state["energy_btn"])
        elif self.state["info"] == "old_food":
            info = self.text["info"]["old_food"]
        elif self.state["info"] == "food_warning":
            info = self.text["info"]["food_warning"].format(self.state["old"],self.state["poisend"])
        self.state["info"] = ""

        # get room description
        room = self.get_room_desc()
        # get quest description
        quest = self.get_quest()
        output = [info, room, quest]
        # shuffle the output for increasing states!
        #self.rng.shuffle(output)
        return " ".join(output)

    def get_location(self):
        return self.rooms[self.state[0]]

    def get_action(self,action):
        return self.actions[action[0]] + " " + self.objects[action[1]]

    def is_executable(self, conditions):
        return all(self.state[f] == v for f,v in conditions.iteritems())

    def is_movement(self,action):
        a,o = action.split(" ")
        return o not in self.env_objects

    def is_terminal(self):
        return (not self.state["quest"]) or self.state["dead"]

    def is_successful(self):
        return self.is_terminal() and not self.state["dead"]

    def do(self, a):
        """
        Action execution function: return next state and reward for executing action
        in current state
        """
        if self.state["dead"]:
            return "You are dead, idiot!", 0
        # check whether action does change the state - executability
        if a in self.definitions:
            for action in self.definitions[a]:
                if not self.is_executable(action["conds"]): continue
                for f,v in action["effs"].iteritems():
                    self.state[f] = v
                if self.is_movement(a):
                    self.state["description"] = self.rng.choice(self.descriptions[self.state["room"]])
                    return self.get_output(), -0.01
                else:
                    obj_desc = self.env_objects[a.split(" ")[1]]
                    r = 1 if self.is_terminal() else -0.01
                    return obj_desc, r
        # if not, return "Nothing happend." and same state description
        return "Nothing happend. " + self.get_output(), -0.1

    def reset(self):
        location = self.rng.choice(self.rooms)
        self.state["room"] = location
        self.state["description"] = self.rng.choice(self.descriptions[location])

        quests = self.permutation(self.quests)
        #quest = self.rng.choice(self.quests)
        #quest_mislead = self.rng.choice(self.quests)
        #if quest_mislead == quest: quest_mislead = ""

        #self.state["quest"] = quest
        #self.state["mislead"] = quest_mislead
        self.state["quest"] = quests[0]
        self.state["mislead"] = quests[1]


        foods = self.permutation(["apple", "cheese", "pizza"])
        self.state["old"] = foods[1]
        self.state["poisoned"] = foods[2]
        self.state["energy"] = False #(self.rng.random() < 0.5)

        recipe = self.permutation(["12", "23", "13"])
        self.state["recipe_good"] = recipe[0]
        self.state["recipe_bad"] = recipe[2]
        self.state["recipies"] = {
            "great":recipe[0],
            "mediocre":recipe[1],
            "bad":recipe[2],
        }

        buttons = self.permutation(["rbutton", "gbutton", "bbutton"])
        self.state["energy_btn"] = buttons[0]
        self.state["shock_btn"] = buttons[1]

        self.state["dead"] = False

        return self.get_output()


class HomeWorldEnv2(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        #
        # Home world
        #
        self.env = HomeWorld2()

        # set the observation space to the vocab size and some kind of sequencial
        # data
        self.observation_space = None
        self.vocab_space = self.env.get_vocab_size()
        # we have a two dimensional discrete action space: action x object
        self.action_space = spaces.Tuple((spaces.Discrete(self.env.num_actions), spaces.Discrete(self.env.num_objects)))
        self.status = ""
        self.last_action = None
        self.last_state = None

    def _step(self, action):
        #a = self.env.actions[action[0]] + " " + self.env.objects[action[1]]
        action = self.env.get_action(action)
        state, reward = self.env.do(action)
        terminal = self.env.is_terminal()

        self.last_action = action
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
    import gym, gym_textgame
    env = gym.make("HomeWorldHard-v0")
    done = False
    states = []
    print env.action_space
    s = env.reset()
    i = 0
    print "({})".format(i), s
    while not done:
        states.append(s)
        i += 1
        a = env.action_space.sample()
        s, r, done, info = env.step(a)
        print "({}) {} {}".format(i, env.env.get_action(a), s)
    print "done!"
    print env.env.state
