# -*- encoding: utf-8 -*-
"""
@Date    :   2023/11/20 11:24:03
@Author  :   orange-crow
@File    :   plan.py
"""
from typing import Union

from metagpt.actions import Action
from metagpt.prompts.plan import TASK_PLAN_SYSTEM_MSG
from metagpt.schema import Message
from metagpt.utils.common import CodeParser


class Plan(Action):
    def __init__(self, llm=None):
        super().__init__("", None, llm)

    async def run(self, prompt: Union[str, Message], role: str = None, system_msg: str = None) -> str:
        if role:
            system_msg = TASK_PLAN_SYSTEM_MSG.format(role=role)
        rsp = self._aask(system_msg + prompt.content) if isinstance(prompt, Message) else await self._aask(system_msg + prompt)
        plan = CodeParser.parse_code(None, rsp).split('\n\n')
        return Message(plan, role="assistant", sent_from=self.__class__.__name__)
