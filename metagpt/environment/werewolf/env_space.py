#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Desc   : werewolf observation/action space and its action definition

from gymnasium import spaces
from pydantic import ConfigDict, Field

from metagpt.environment.base_env_space import BaseEnvAction, BaseEnvActionType
from metagpt.environment.werewolf.const import STEP_INSTRUCTIONS, RoleState


class EnvActionType(BaseEnvActionType):
    NONE = 0  # no action to run, just get observation
    WOLF_KILL = 1  # wolf kill someone
    VOTE_KILL = 2  # vote kill someone
    WITCH_POISON = 3  # witch poison someone
    WITCH_SAVE = 4  # witch save someone
    GUARD_PROTECT = 5  # guard protect someone
    PROGRESS_STEP = 6  # step increment


class EnvAction(BaseEnvAction):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    action_type: int = Field(default=EnvActionType.NONE, description="action type")
    player_name: str = Field(default="", description="the name of the player to do the action")
    target_player_name: str = Field(default="", description="the name of the player who take the action")


def get_observation_space(player_num: int) -> spaces.Dict:
    space = spaces.Dict(
        {
            "step_idx": spaces.Discrete(len(STEP_INSTRUCTIONS)),
            "player_states": spaces.MultiDiscrete([len(RoleState)] * player_num),
            "vote_counts": spaces.MultiDiscrete([player_num - 1] * player_num),
            "player_current_dead": None,  # TODO
            "winner": spaces.Text(16),
            "win_reason": spaces.Text(64),
        }
    )
    return space


def get_action_space() -> spaces.Dict:
    space = spaces.Dict(
        {
            "action_type": spaces.Discrete(len(EnvActionType)),
            "player_name": spaces.Text(16),  # the player to do the action
            "target_player_name": spaces.Text(16),  # the target player who take the action
        }
    )
    return space
