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
