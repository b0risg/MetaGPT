#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/11 14:43
@Author  : alexanderwu
@File    : action.py
"""

from abc import ABC
from typing import Optional

from tenacity import retry, stop_after_attempt, wait_fixed, after_log

from metagpt.actions.action_output import ActionOutput
from metagpt.llm import LLM
from metagpt.logs import logger
from metagpt.utils.common import OutputParser
from metagpt.utils.repair_llm_raw_output import repair_llm_raw_output, RepairType,\
    retry_parse_json_text, extract_content_from_output


class Action(ABC):
    def __init__(self, name: str = "", context=None, llm: LLM = None):
        self.name: str = name
        if llm is None:
            llm = LLM()
        self.llm = llm
        self.context = context
        self.prefix = ""
        self.profile = ""
        self.desc = ""
        self.content = ""
        self.instruct_content = None

    def set_prefix(self, prefix, profile):
        """Set prefix for later usage"""
        self.prefix = prefix
        self.profile = profile

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return self.__str__()

    async def _aask(self, prompt: str, system_msgs: Optional[list[str]] = None) -> str:
        """Append default prefix"""
        if not system_msgs:
            system_msgs = []
        system_msgs.append(self.prefix)
        return await self.llm.aask(prompt, system_msgs)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(1),
        after=after_log(logger, logger.level("ERROR").name),
    )
    async def _aask_v1(
        self,
        prompt: str,
        output_class_name: str,
        output_data_mapping: dict,
        system_msgs: Optional[list[str]] = None,
        format="markdown",  # compatible to original format
    ) -> ActionOutput:
        """Append default prefix"""
        if not system_msgs:
            system_msgs = []
        system_msgs.append(self.prefix)
        content = await self.llm.aask(prompt, system_msgs)
        logger.debug(f"llm raw output:\n{content}")
        output_class = ActionOutput.create_model_class(output_class_name, output_data_mapping)
        output_class_fields = list(output_class.schema()["properties"].keys())  # Custom ActionOutput's fields

        if format == "json":
            content = repair_llm_raw_output(content, req_keys=output_class_fields + ["[/CONTENT]"])
            content = extract_content_from_output(content)
            content = repair_llm_raw_output(content, req_keys=[None], repair_type=RepairType.JSON)  # req_keys mocked
            logger.info(f"extracted json CONTENT from output:\n{content}")
            parsed_data = retry_parse_json_text(output=content)  # should use output=content

        else:  # using markdown parser
            parsed_data = OutputParser.parse_data_with_mapping(content, output_data_mapping)

        logger.debug(f"parsed_data:\n{parsed_data}")
        instruct_content = output_class(**parsed_data)
        return ActionOutput(content, instruct_content)

    async def run(self, *args, **kwargs):
        """Run action"""
        raise NotImplementedError("The run method should be implemented in a subclass.")
