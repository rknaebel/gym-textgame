import logging
from gym.envs.registration import register

logger = logging.getLogger(__name__)

register(
    id='HomeWorldSmall-v0',
    entry_point='gym_textgame.envs:HomeWorld0',
    timestep_limit=10,
    reward_threshold=1.0,
    nondeterministic = False,
)
register(
    id='HomeWorld-v0',
    entry_point='gym_textgame.envs:HomeWorld1',
    timestep_limit=100,
    reward_threshold=1.0,
    nondeterministic = False,
)

register(
    id='HomeWorldHard-v0',
    entry_point='gym_textgame.envs:HomeWorld2',
    timestep_limit=100,
    reward_threshold=1.0,
    nondeterministic = False,
)
register(
    id='HomeWorldHardSmall-v0',
    entry_point='gym_textgame.envs:HomeWorld3',
    timestep_limit=20,
    reward_threshold=1.0,
    nondeterministic = False,
)

register(
    id='HomeWorld4-v0',
    entry_point='gym_textgame.envs:HomeWorld4',
    timestep_limit=20,
    reward_threshold=1.0,
    nondeterministic = False,
)

register(
    id='HomeWorld5-v0',
    entry_point='gym_textgame.envs:HomeWorld5',
    timestep_limit=20,
    reward_threshold=1.0,
    nondeterministic = False,
)

