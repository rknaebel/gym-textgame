import os, subprocess, time, signal, sys
import random

from textgame import HomeWorld
from gym import spaces, error, utils

#import spacy
import re

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

class HomeWorld1(HomeWorld):
    def __init__(self):
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
        }

        self.rooms = self.descriptions.keys()

        self.env_objects = {
            "tv" : "A huge television that is great for watching games.",
            "bike" : "A nice shiny bike that is fun to ride.",
            "apple" : "A red juicy fruit.",
            "bed" : "A nice, comfortable bed with pillows and sheets."
        }

        self.definitions = {
            ("eat apple") :  [{
                "conds" :{"room":"kitchen", "quest":"hungry"},
                "effs"  :{"quest":""}
                },{
                "conds" :{"room":"kitchen",},
                "effs"  :{}
            }],
            ("exercise bike") :  [{
                "conds" :{"room":"garden", "quest":"fat"},
                "effs"  :{"quest":""}
                },{
                "conds" :{"room":"garden",},
                "effs"  :{}
            }],
            ("sleep bed") :  [{
                "conds" :{"room":"bedroom", "quest":"sleepy"},
                "effs"  :{"quest":""}
                },{
                "conds" :{"room":"bedroom",},
                "effs"  :{}
            }],
            ("watch tv") : [{
                "conds" : {"room":"living", "quest":"bored"},
                "effs"    : {"quest":""}
                },{
                "conds" : {"room":"living"},
                "effs"    : {}
            }],

            #
            # Move in direction
            #
            ("go north") : [
                {"conds":{"room":"bedroom"}, "effs":{"room":"living"}},
                {"conds":{"room":"kitchen"}, "effs":{"room":"garden"}},
            ],
            ("go south") : [
                {"conds":{"room":"living"}, "effs":{"room":"bedroom"}},
                {"conds":{"room":"garden"}, "effs":{"room":"kitchen"}},
            ],
            ("go east") : [
                {"conds":{"room":"living"}, "effs":{"room":"garden"}},
                {"conds":{"room":"bedroom"}, "effs":{"room":"kitchen"}},
            ],
            ("go west") : [
                {"conds":{"room":"garden"}, "effs":{"room":"living"}},
                {"conds":{"room":"kitchen"}, "effs":{"room":"bedroom"}},
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
        }

        HomeWorld.__init__(self)

        self.actions = list({a.split(" ")[0] for a in self.definitions})
        self.objects = list({a.split(" ")[1] for a in self.definitions})

        self.num_actions = len(self.actions)
        self.num_objects = len(self.objects)

        self.quests = self.text["quest"].keys()
        self.extra_vocab = ['nothing', 'happend', 'not', 'but', 'now']

        self.state = {
            "room" : "",
            "description" : "",
            "quest" : "",
            "mislead" : "",
        }

        self.init_vocab()
        # set the observation space to the vocab size and some kind of sequencial
        # data
        self.vocab_space = self.get_vocab_size()
        self.action_space = spaces.Tuple((spaces.Discrete(self.num_actions), spaces.Discrete(self.num_objects)))
        self.observation_space = None
        self.seq_length = 30



    def init_vocab(self):
        words = u" ".join(  [d for ds in self.descriptions.values() for d in ds] +
                            self.env_objects.values() +
                            [t for k,v in self.text.iteritems() for t in v.values()] +
                            self.extra_vocab
        )
        words = re.sub(r'[^\w\s]','',words)
        self.vocab = set(re.split(r'\s*', words))

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
        # get room description
        room = self.get_room_desc()
        # get quest description
        quest = self.get_quest()
        output = [room, quest]
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
        return (not self.state["quest"])

    def is_successful(self):
        return self.is_terminal()

    def do(self, a):
        """
        Action execution function: return next state and reward for executing action
        in current state
        """
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
                    obj = a.split(" ")[1]
                    out = self.env_objects[obj]
                    if self.is_terminal():
                        if self.is_successful():
                            r = 1
                        else:
                            r = -1
                    else:
                        r = -0.01
                    #r = 1 if self.is_terminal() else -0.01
                    return out, r
        # if not, return "Nothing happend." and same state description
        return "Nothing happend. " + self.get_output(), -0.1

    def reset(self):
        location = self.rng.choice(self.rooms)
        self.state["room"] = location
        self.state["description"] = self.rng.choice(self.descriptions[location])

        quests = self.permutation(self.quests)
        self.state["quest"] = quests[0]
        self.state["mislead"] = quests[1]

        return self.get_output()


def main():
    import gym, gym_textgame
    env = gym.make("HomeWorld-v0")
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
    print "done!", r
    print env.env.state

def test():
    env = HomeWorld1()
    done = False
    print env.reset()
    while not done:
        action = raw_input(">> ")
        if action == "help":
            print env.definitions.keys()
            continue
        elif action == "help state":
            print env.state
            continue
        else:
            state, reward = env.do(action)
            done = env.is_terminal()
            print state
    print "you are done!"
    if env.is_successful():
        print "congrats!"
    else:
        print "sorry dude, you are dead..."

if __name__ == "__main__":
    test()
