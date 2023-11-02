#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023-11-1
@Author  : mashenquan
@File    : test_role.py
"""
import pytest
from pydantic import BaseModel

from metagpt.actions import Action, ActionOutput
from metagpt.environment import Environment
from metagpt.roles import Role
from metagpt.schema import Message


class MockAction(Action):
    async def run(self, messages, *args, **kwargs):
        assert messages
        return ActionOutput(content=messages[-1].content, instruct_content=messages[-1])


class MockRole(Role):
    def __init__(self, name="", profile="", goal="", constraints="", desc=""):
        super().__init__(name=name, profile=profile, goal=goal, constraints=constraints, desc=desc)
        self._init_actions([MockAction()])


@pytest.mark.asyncio
async def test_react():
    class Input(BaseModel):
        name: str
        profile: str
        goal: str
        constraints: str
        desc: str
        subscription: str

    inputs = [
        {
            "name": "A",
            "profile": "Tester",
            "goal": "Test",
            "constraints": "constraints",
            "desc": "desc",
            "subscription": "start",
        }
    ]

    for i in inputs:
        seed = Input(**i)
        role = MockRole(
            name=seed.name, profile=seed.profile, goal=seed.goal, constraints=seed.constraints, desc=seed.desc
        )
        role.subscribe({seed.subscription})
        assert role._rc.watch == {seed.subscription}
        assert role.name == seed.name
        assert role.profile == seed.profile
        assert role.is_idle
        env = Environment()
        env.add_role(role)
        env.publish_message(Message(content="test", cause_by=seed.subscription))
        assert not role.is_idle
        while not env.is_idle:
            await env.run()
        assert role.is_idle


if __name__ == "__main__":
    pytest.main([__file__, "-s"])
