#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : alexanderwu
@File    : summarize_code.py
@Modified By: mashenquan, 2023/12/5. Archive the summarization content of issue discovery for use in WriteCode.
"""
from pathlib import Path

from pydantic import Field
from tenacity import retry, stop_after_attempt, wait_random_exponential

from metagpt.actions.action import Action
from metagpt.config import CONFIG
from metagpt.const import SYSTEM_DESIGN_FILE_REPO, TASK_FILE_REPO
from metagpt.llm import LLM, BaseGPTAPI
from metagpt.logs import logger
from metagpt.schema import CodeSummarizeContext
from metagpt.utils.file_repository import FileRepository

PROMPT_TEMPLATE = """
NOTICE
Role: You are a professional software engineer, and your main task is to review the code.
Language: Please use the same language as the user requirement, but the title and code should be still in English. For example, if the user speaks Chinese, the specific text of your answer should also be in Chinese.
ATTENTION: Use '##' to SPLIT SECTIONS, not '#'. Output format carefully referenced "Format example".

-----
# System Design
```text
{system_design}
```
-----
# Tasks
```text
{tasks}
```
-----
{code_blocks}

## Code Review All: Please read all historical files and find possible bugs in the files, such as unimplemented functions, calling errors, unreferences, etc.

## Call flow: mermaid code, based on the implemented function, use mermaid to draw a complete call chain

## Summary: Summary based on the implementation of historical files

## TODOs: Python dict[str, str], write down the list of files that need to be modified and the reasons. We will modify them later.

"""

FORMAT_EXAMPLE = """

## Code Review All

### a.py
- It fulfills less of xxx requirements...
- Field yyy is not given...
-...

### b.py
...

### c.py
...

## Call flow
```mermaid
flowchart TB
    c1-->a2
    subgraph one
    a1-->a2
    end
    subgraph two
    b1-->b2
    end
    subgraph three
    c1-->c2
    end
```

## Summary
- a.py:...
- b.py:...
- c.py:...
- ...

## TODOs
{
    "a.py": "implement requirement xxx...",
}

"""


# TOTEST
class SummarizeCode(Action):
    name: str = "SummarizeCode"
    context: CodeSummarizeContext = Field(default_factory=CodeSummarizeContext)
    llm: BaseGPTAPI = Field(default_factory=LLM)

    @retry(stop=stop_after_attempt(2), wait=wait_random_exponential(min=1, max=60))
    async def summarize_code(self, prompt):
        code_rsp = await self._aask(prompt)
        return code_rsp

    async def run(self):
        design_pathname = Path(self.context.design_filename)
        design_doc = await FileRepository.get_file(filename=design_pathname.name, relative_path=SYSTEM_DESIGN_FILE_REPO)
        task_pathname = Path(self.context.task_filename)
        task_doc = await FileRepository.get_file(filename=task_pathname.name, relative_path=TASK_FILE_REPO)
        src_file_repo = CONFIG.git_repo.new_file_repository(relative_path=CONFIG.src_workspace)
        code_blocks = []
        for filename in self.context.codes_filenames:
            code_doc = await src_file_repo.get(filename)
            code_block = f"```python\n{code_doc.content}\n```\n-----"
            code_blocks.append(code_block)
        format_example = FORMAT_EXAMPLE
        prompt = PROMPT_TEMPLATE.format(
            system_design=design_doc.content,
            tasks=task_doc.content,
            code_blocks="\n".join(code_blocks),
            format_example=format_example,
        )
        logger.info("Summarize code..")
        rsp = await self.summarize_code(prompt)
        return rsp
