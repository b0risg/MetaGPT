import pytest

from metagpt.provider.openai_api import OpenAIGPTAPI
from metagpt.schema import UserMessage


@pytest.mark.asyncio
async def test_aask_code():
    llm = OpenAIGPTAPI()
    msg = [{"role": "user", "content": "Write a python hello world code."}]
    rsp = await llm.aask_code(msg)  # -> {'language': 'python', 'code': "print('Hello, World!')"}
    assert "language" in rsp
    assert "code" in rsp
    assert len(rsp["code"]) > 0


@pytest.mark.asyncio
async def test_aask_code_str():
    llm = OpenAIGPTAPI()
    msg = "Write a python hello world code."
    rsp = await llm.aask_code(msg)  # -> {'language': 'python', 'code': "print('Hello, World!')"}
    assert "language" in rsp
    assert "code" in rsp
    assert len(rsp["code"]) > 0


@pytest.mark.asyncio
async def test_aask_code_Message():
    llm = OpenAIGPTAPI()
    msg = UserMessage("Write a python hello world code.")
    rsp = await llm.aask_code(msg)  # -> {'language': 'python', 'code': "print('Hello, World!')"}
    assert "language" in rsp
    assert "code" in rsp
    assert len(rsp["code"]) > 0


def test_ask_code():
    llm = OpenAIGPTAPI()
    msg = [{"role": "user", "content": "Write a python hello world code."}]
    rsp = llm.ask_code(msg)  # -> {'language': 'python', 'code': "print('Hello, World!')"}
    assert "language" in rsp
    assert "code" in rsp
    assert len(rsp["code"]) > 0


def test_ask_code_str():
    llm = OpenAIGPTAPI()
    msg = "Write a python hello world code."
    rsp = llm.ask_code(msg)  # -> {'language': 'python', 'code': "print('Hello, World!')"}
    assert "language" in rsp
    assert "code" in rsp
    assert len(rsp["code"]) > 0


def test_ask_code_Message():
    llm = OpenAIGPTAPI()
    msg = UserMessage("Write a python hello world code.")
    rsp = llm.ask_code(msg)  # -> {'language': 'python', 'code': "print('Hello, World!')"}
    assert "language" in rsp
    assert "code" in rsp
    assert len(rsp["code"]) > 0


def test_ask_code_list_Message():
    llm = OpenAIGPTAPI()
    msg = [UserMessage("a=[1,2,5,10,-10]"), UserMessage("写出求a中最大值的代码python")]
    rsp = llm.ask_code(msg)  # -> {'language': 'python', 'code': 'max_value = max(a)\nmax_value'}
    assert "language" in rsp
    assert "code" in rsp
    assert len(rsp["code"]) > 0


def test_ask_code_list_str():
    llm = OpenAIGPTAPI()
    msg = ["a=[1,2,5,10,-10]", "写出求a中最大值的代码python"]
    rsp = llm.ask_code(msg)  # -> {'language': 'python', 'code': 'max_value = max(a)\nmax_value'}
    print(rsp)
    assert "language" in rsp
    assert "code" in rsp
    assert len(rsp["code"]) > 0


@pytest.mark.asyncio
async def test_ask_code_steps2():
    llm = OpenAIGPTAPI()
    msg = ["step by setp 生成代码: Step 1. 先生成随机数组a, Step 2. 求a中最大值, Step 3. 绘制数据a的直方图"]
    rsp = await llm.aask_code(msg)  # -> {'language': 'python', 'code': 'max_value = max(a)\nmax_value'}
    print(rsp)
    assert "language" in rsp
    assert "code" in rsp
    assert len(rsp["code"]) > 0
    assert "Step 1" in rsp["code"]
    assert "Step 2" in rsp["code"]
    assert "Step 3" in rsp["code"]
