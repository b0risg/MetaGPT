#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""
@Time    : 2023/9/4 15:40:40
@Author  : Stitch-z
@File    : tutorial_assistant.py
@Describe : Actions of the tutorial assistant, including writing directories and document content.
"""
import json
from typing import Dict

from metagpt.actions import Action
from metagpt.logs import logger
from metagpt.prompts.tutorial_assistant import DIRECTORY_PROMPT, CONTENT_PROMPT


class WriteDirectory(Action):
    """Action class for writing tutorial directories.

    Args:
        name: The name of the action.
        language: The language to output, default is "Chinese".
    """

    def __init__(self, name: str = "", language: str = "Chinese", *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.language = language

    @staticmethod
    async def _handle_resp(resp: str) -> Dict:
        """Process string results and convert them to JSON format.

        Args:
            resp: The directory results returned by gpt.

        Returns:
            The parsed dictionary, such as {"title": "xxx", "directory": [{"dir 1": ["sub dir 1", "sub dir 2"]}]}.

        Raises:
            Exception: If no matching dictionary section is found.
            json.JSONDecodeError: If the dictionary part cannot be parsed as JSON.
        """
        start = resp.find('{')
        end = resp.rfind('}')
        if start != -1 and end != -1 and end > start:
            directory_str = resp[start:end + 1]
            logger.info(f"Successfully parsed json: {str(directory_str)}")
            try:
                return json.loads(directory_str)
            except json.JSONDecodeError as e:
                logger.error(f"Json parsing error: {e}")
                raise e
        else:
            raise Exception("No matching dictionary section found.")

    async def run(self, topic: str, *args, **kwargs) -> Dict:
        """Execute the action to generate a tutorial directory according to the topic.

        Args:
            topic: The tutorial topic.

        Returns:
            the tutorial directory information, including {"title": "xxx", "directory": [{"dir 1": ["sub dir 1", "sub dir 2"]}]}.
        """
        prompt = DIRECTORY_PROMPT.format(topic=topic, language=self.language)
        resp = await self._aask(prompt=prompt)
        return await self._handle_resp(resp)


class WriteContent(Action):
    """Action class for writing tutorial content.

    Args:
        name: The name of the action.
        directory: The content to write.
        language: The language to output, default is "Chinese".
    """

    def __init__(self, name: str = "", directory: str = "", language: str = "Chinese", *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.language = language
        self.directory = directory

    async def run(self, topic: str, *args, **kwargs) -> str:
        """Execute the action to write document content according to the directory and topic.

        Args:
            topic: The tutorial topic.

        Returns:
            The written tutorial content.
        """
        prompt = CONTENT_PROMPT.format(topic=topic, language=self.language, directory=self.directory)
        return await self._aask(prompt=prompt)

