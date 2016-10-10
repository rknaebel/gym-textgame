import os, subprocess, time, signal
import random
#random.seed(42)

import gym
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

        #self.actions = ["eat", "sleep", "watch", "exercise", "go"]
        self.action_meanings = ["go " + d for d in self.moves.keys()] + ["{} {}".format(a,o) for o,(_,a,_) in self.env_objects.items()]
        #self.objects = self.env_objects.keys() + self.moves.keys()
        self.num_actions = len(self.action_meanings)
        self.rooms = self.descriptions.keys()
        self.quests = ['You are hungry','You are sleepy', 'You are bored', 'You are getting fat']
        self.quests_mislead = ['You are not hungry','You are not sleepy', 'You are not bored', 'You are not getting fat']

        self.quest_actions = ['eat', 'sleep', 'watch' ,'exercise']
        #self.quest_checklist = []
        #self.mislead_quest_checklist = []

        self.extra_vocab = ['not','but', 'now']

        self.state = None

        # reset and initialize environment

    def get_vocab_size(self):
        words = ([d for ds in self.descriptions.values() for d in ds] +
                 [d[2] for d in self.env_objects.values()] +
                 self.rooms +
                 self.action_meanings +
                 self.quests +
                 self.extra_vocab)
        self.vocab = reduce(lambda x,y: x | y, (set(d.split()) for d in words))
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
                        self.state[1] = random.randint(0,2)
                        return self.get_output(), 0
            else:
                obj_desc = self.env_objects[obj][2]
                r = 1 if self.quest_actions.index(action) == self.state[2] else 0
                if r == 1: self.state[2] = -1
                return obj_desc, r
        # if not, return "Nothing happend." and same state description
        else:
            return "Nothing happend. " + self.get_output(), 0

    def reset(self):
        location = random.randint(0,len(self.rooms)-1)
        location_desc = random.randint(0,2)
        quest = random.randint(0,len(self.quests)-1)
        quest_mislead = random.randint(0,len(self.quests)-1)
        if quest_mislead == quest: quest_mislead = -1

        self.state = [location, location_desc, quest, quest_mislead]
        return self.get_output()


#env = HomeWorld()
#print env.reset()
#while True:
#    print env.state
#    print env.action_meanings
#    action,obj = raw_input(">").split(" ")
#    print env.do(action,obj)
#

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
        # we have a two dimensional discrete action space: action x object
        #self.action_space = spaces.Tuple((spaces.Discrete(self.env.num_actions),
        #                                  spaces.Discrete(self.env.num_objects)))
        self.action_space = spaces.Discrete(self.env.num_actions)
        self.status = ""

    def get_action_meanings(self):
        return self.env.action_meanings

    def _step(self, action):
        pass

    def _reset(self):
        return self.env.reset()

    def _render(self, mode="human", close=False):
        pass

env = HomeWorldEnv()

class SoccerEnv(gym.Env, utils.EzPickle):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.viewer = None
        self.server_process = None
        self.server_port = None
        self.hfo_path = hfo_py.get_hfo_path()
        self._configure_environment()
        self.env = hfo_py.HFOEnvironment()
        self.env.connectToServer(config_dir=hfo_py.get_config_path())
        self.observation_space = spaces.Box(low=-1, high=1,
                                            shape=(self.env.getStateSize()))
        # Action space omits the Tackle/Catch actions, which are useful on defense
        self.action_space = spaces.Tuple((spaces.Discrete(3),
                                          spaces.Box(low=0, high=100, shape=1),
                                          spaces.Box(low=-180, high=180, shape=1),
                                          spaces.Box(low=-180, high=180, shape=1),
                                          spaces.Box(low=0, high=100, shape=1),
                                          spaces.Box(low=-180, high=180, shape=1)))
        self.status = hfo_py.IN_GAME

    def __del__(self):
        self.env.act(hfo_py.QUIT)
        self.env.step()
        os.kill(self.server_process.pid, signal.SIGINT)
        if self.viewer is not None:
            os.kill(self.viewer.pid, signal.SIGKILL)

    def _configure_environment(self):
        """
        Provides a chance for subclasses to override this method and supply
        a different server configuration. By default, we initialize one
        offense agent against no defenders.
        """
        self._start_hfo_server()

    def _start_hfo_server(self, frames_per_trial=500,
                          untouched_time=100, offense_agents=1,
                          defense_agents=0, offense_npcs=0,
                          defense_npcs=0, sync_mode=True, port=6000,
                          offense_on_ball=0, fullstate=True, seed=-1,
                          ball_x_min=0.0, ball_x_max=0.2,
                          verbose=False, log_game=False,
                          log_dir="log"):
        """
        Starts the Half-Field-Offense server.
        frames_per_trial: Episodes end after this many steps.
        untouched_time: Episodes end if the ball is untouched for this many steps.
        offense_agents: Number of user-controlled offensive players.
        defense_agents: Number of user-controlled defenders.
        offense_npcs: Number of offensive bots.
        defense_npcs: Number of defense bots.
        sync_mode: Disabling sync mode runs server in real time (SLOW!).
        port: Port to start the server on.
        offense_on_ball: Player to give the ball to at beginning of episode.
        fullstate: Enable noise-free perception.
        seed: Seed the starting positions of the players and ball.
        ball_x_[min/max]: Initialize the ball this far downfield: [0,1]
        verbose: Verbose server messages.
        log_game: Enable game logging. Logs can be used for replay + visualization.
        log_dir: Directory to place game logs (*.rcg).
        """
        self.server_port = port
        cmd = self.hfo_path + \
              " --headless --frames-per-trial %i --untouched-time %i --offense-agents %i"\
              " --defense-agents %i --offense-npcs %i --defense-npcs %i"\
              " --port %i --offense-on-ball %i --seed %i --ball-x-min %f"\
              " --ball-x-max %f --log-dir %s"\
              % (frames_per_trial, untouched_time, offense_agents,
                 defense_agents, offense_npcs, defense_npcs, port,
                 offense_on_ball, seed, ball_x_min, ball_x_max,
                 log_dir)
        if not sync_mode: cmd += " --no-sync"
        if fullstate:     cmd += " --fullstate"
        if verbose:       cmd += " --verbose"
        if not log_game:  cmd += " --no-logging"
        print('Starting server with command: %s' % cmd)
        self.server_process = subprocess.Popen(cmd.split(' '), shell=False)
        time.sleep(10) # Wait for server to startup before connecting a player

    def _start_viewer(self):
        """
        Starts the SoccerWindow visualizer. Note the viewer may also be
        used with a *.rcg logfile to replay a game. See details at
        https://github.com/LARG/HFO/blob/master/doc/manual.pdf.
        """
        cmd = hfo_py.get_viewer_path() +\
              " --connect --port %d" % (self.server_port)
        self.viewer = subprocess.Popen(cmd.split(' '), shell=False)

    def _step(self, action):
        self._take_action(action)
        self.status = self.env.step()
        reward = self._get_reward()
        ob = self.env.getState()
        episode_over = self.status != hfo_py.IN_GAME
        return ob, reward, episode_over, {}

    def _take_action(self, action):
        """ Converts the action space into an HFO action. """
        action_type = ACTION_LOOKUP[action[0]]
        if action_type == hfo_py.DASH:
            self.env.act(action_type, action[1], action[2])
        elif action_type == hfo_py.TURN:
            self.env.act(action_type, action[3])
        elif action_type == hfo_py.KICK:
            self.env.act(action_type, action[4], action[5])
        else:
            print('Unrecognized action %d' % action_type)
            self.env.act(hfo_py.NOOP)

    def _get_reward(self):
        """ Reward is given for scoring a goal. """
        if self.status == hfo_py.GOAL:
            return 1
        else:
            return 0

    def _reset(self):
        """ Repeats NO-OP action until a new episode begins. """
        while self.status == hfo_py.IN_GAME:
            self.env.act(hfo_py.NOOP)
            self.status = self.env.step()
        while self.status != hfo_py.IN_GAME:
            self.env.act(hfo_py.NOOP)
            self.status = self.env.step()
        return self.env.getState()

    def _render(self, mode='human', close=False):
        """ Viewer only supports human mode currently. """
        if close:
            if self.viewer is not None:
                os.kill(self.viewer.pid, signal.SIGKILL)
        else:
            if self.viewer is None:
                self._start_viewer()
