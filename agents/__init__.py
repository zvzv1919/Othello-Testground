from gymnasium.envs.registration import register

register(
    id='agents-v0',
    entry_point='agents.envs:OthelloEnv',
)
