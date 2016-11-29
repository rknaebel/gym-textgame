import logging
from gym.envs.registration import register

logger = logging.getLogger(__name__)

register(
    id='HomeWorld-v0',
    entry_point='gym_textgame.envs:HomeWorldEnv',
    timestep_limit=100,
    reward_threshold=1.0,
    nondeterministic = False,
)

register(
    id='HomeWorldHard-v0',
    entry_point='gym_textgame.envs:HomeWorldEnv2',
    timestep_limit=100,
    reward_threshold=1.0,
    nondeterministic = False,
)
register(
    id='HomeWorldHardSmall-v0',
    entry_point='gym_textgame.envs:HomeWorldEnv3',
    timestep_limit=20,
    reward_threshold=1.0,
    nondeterministic = False,
)
