#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/9/16 20:03
@Author  : femto Zheng
@File    : test_basic_planner.py
"""
import os

import pytest
from semantic_kernel.core_skills import FileIOSkill, MathSkill, TextSkill, TimeSkill
from semantic_kernel.planning.action_planner.action_planner import ActionPlanner

from metagpt.actions import BossRequirement
from metagpt.roles.sk_agent import SkAgent
from metagpt.schema import Message

# Get the directory of the current file
current_file_directory = os.path.dirname(os.path.abspath(__file__))
# Construct the skills_directory by joining the parent directory and "skillss"
skills_directory = os.path.join(current_file_directory, "..", "skills")
# Normalize the path to ensure it's in the correct format
skills_directory = os.path.normpath(skills_directory)


@pytest.mark.asyncio
async def test_action_planner():
    role = SkAgent(planner_cls=ActionPlanner)
    # let's give the agent 4 skills
    role.import_skill(MathSkill(), "math")
    role.import_skill(FileIOSkill(), "fileIO")
    role.import_skill(TimeSkill(), "time")
    role.import_skill(TextSkill(), "text")
    task = "What is the sum of 110 and 990?"
    role.recv(Message(content=task, cause_by=BossRequirement))

    await role._think()  # it will choose mathskill.Add
    assert "1100" == (await role._act()).content
