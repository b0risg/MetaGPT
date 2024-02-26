# -*- encoding: utf-8 -*-
"""
@Date    :   2023/11/20 11:24:03
@Author  :   orange-crow
@File    :   plan.py
"""
from __future__ import annotations

import json
from copy import deepcopy
from typing import Tuple

from metagpt.actions import Action
from metagpt.logs import logger
from metagpt.schema import Message, Plan, Task
from metagpt.tools import TOOL_REGISTRY
from metagpt.utils.common import CodeParser


class WritePlan(Action):
    PROMPT_TEMPLATE: str = """
    # Context:
    __context__
    # Available Task Types:
    __task_type_desc__
    # Task:
    Based on the context, write a plan or modify an existing plan of what you should do to achieve the goal. A plan consists of one to __max_tasks__ tasks.
    If you are modifying an existing plan, carefully follow the instruction, don't make unnecessary changes. Give the whole plan unless instructed to modify only one task of the plan.
    If you encounter errors on the current task, revise and output the current single task only.
    Output a list of jsons following the format:
    ```json
    [
        {
            "task_id": str = "unique identifier for a task in plan, can be an ordinal",
            "dependent_task_ids": list[str] = "ids of tasks prerequisite to this task",
            "instruction": "what you should do in this task, one short phrase or sentence",
            "task_type": "type of this task, should be one of Available Task Types",
        },
        ...
    ]
    ```
    """

    async def run(self, context: list[Message], max_tasks: int = 5, use_tools: bool = False) -> str:
        task_type_desc = "\n".join(
            [f"- **{tool_type.name}**: {tool_type.desc}" for tool_type in TOOL_REGISTRY.get_tool_types().values()]
        )  # task type are binded with tool type now, should be improved in the future
        prompt = (
            self.PROMPT_TEMPLATE.replace("__context__", "\n".join([str(ct) for ct in context]))
            # .replace("__current_plan__", current_plan)
            .replace("__max_tasks__", str(max_tasks)).replace("__task_type_desc__", task_type_desc)
        )
        rsp = await self._aask(prompt)
        rsp = CodeParser.parse_code(block=None, text=rsp)
        return rsp


def rsp_to_tasks(rsp: str) -> list[Task]:
    rsp = json.loads(rsp)
    tasks = [Task(**task_config) for task_config in rsp]
    return tasks


def update_plan_from_rsp(rsp: str, current_plan: Plan):
    tasks = rsp_to_tasks(rsp)
    if len(tasks) == 1 or tasks[0].dependent_task_ids:
        if tasks[0].dependent_task_ids and len(tasks) > 1:
            # tasks[0].dependent_task_ids means the generated tasks are not a complete plan
            # for they depend on tasks in the current plan, in this case, we only support updating one task each time
            logger.warning(
                "Current plan will take only the first generated task if the generated tasks are not a complete plan"
            )
        # handle a single task
        if current_plan.has_task_id(tasks[0].task_id):
            # replace an existing task
            current_plan.replace_task(tasks[0])
        else:
            # append one task
            current_plan.append_task(tasks[0])

    else:
        # add tasks in general
        current_plan.add_tasks(tasks)


def precheck_update_plan_from_rsp(rsp: str, current_plan: Plan) -> Tuple[bool, str]:
    temp_plan = deepcopy(current_plan)
    try:
        update_plan_from_rsp(rsp, temp_plan)
        return True, ""
    except Exception as e:
        return False, e
