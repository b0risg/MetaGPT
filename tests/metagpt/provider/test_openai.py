import pytest
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionMessage,
    ChatCompletionMessageToolCall,
)
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_message_tool_call import Function

from metagpt.const import TEST_DATA_PATH
from metagpt.llm import LLM
from metagpt.logs import logger
from metagpt.provider import OpenAILLM
from tests.metagpt.provider.mock_llm_config import (
    mock_llm_config,
    mock_llm_config_proxy,
)


@pytest.mark.asyncio
async def test_text_to_speech():
    llm = LLM()
    resp = await llm.atext_to_speech(
        model="tts-1",
        voice="alloy",
        input="人生说起来长，但直到一个岁月回头看，许多事件仅是仓促的。一段一段拼凑一起，合成了人生。苦难当头时，当下不免觉得是折磨；回头看，也不够是一段短短的人生旅程。",
    )
    assert 200 == resp.response.status_code


@pytest.mark.asyncio
async def test_speech_to_text():
    llm = LLM()
    audio_file = open(f"{TEST_DATA_PATH}/audio/hello.mp3", "rb")
    resp = await llm.aspeech_to_text(file=audio_file, model="whisper-1")
    assert "你好" == resp.text


class TestOpenAI:
    def test_make_client_kwargs_without_proxy(self):
        instance = OpenAILLM(mock_llm_config)
        kwargs = instance._make_client_kwargs()
        assert kwargs["api_key"] == "mock_api_key"
        assert kwargs["base_url"] == "mock_base_url"
        assert "http_client" not in kwargs

    def test_make_client_kwargs_with_proxy(self):
        instance = OpenAILLM(mock_llm_config_proxy)
        kwargs = instance._make_client_kwargs()
        assert "http_client" in kwargs

    def test_get_choice_function_arguments_for_aask_code(self, tool_calls_rsp):
        instance = OpenAILLM()
        for i, rsp in enumerate(tool_calls_rsp):
            code = instance.get_choice_function_arguments(rsp)
            logger.info(f"\ntest get function call arguments {i}: {code}")
            assert "code" in code
            assert "language" in code
            assert "hello world" in code["code"]
            logger.info(f'code is : {code["code"]}')

            if "Completed a python code for hello world!" == code["code"]:
                code["language"] == "markdown"
            else:
                code["language"] == "python"

    def test_make_client_kwargs_without_proxy_azure(self, config_azure):
        instance = OpenAILLM()
        instance.config = config_azure

    @pytest.fixture
    def tool_calls_rsp(self):
        function_rsps = [
            Function(arguments='{\n"language": "python",\n"code": "print(\'hello world\')"}', name="execute"),
            Function(arguments='{\n"language": "python",\n"code": \'print("hello world")\'}', name="execute"),
            Function(arguments='{\n"language": \'python\',\n"code": "print(\'hello world\')"}', name="execute"),
            Function(arguments='{\n"language": "python",\n"code": "print(\'hello world\')"}', name="execute"),
            Function(arguments='{\n"language": "python",\n"code": ```print("hello world")```}', name="execute"),
            Function(arguments='{\n"language": "python",\n"code": """print("hello world")"""}', name="execute"),
            Function(arguments='\nprint("hello world")\\n', name="execute"),
            # only `{` in arguments
            Function(arguments='{\n"language": "python",\n"code": "print(\'hello world\')"', name="execute"),
            # no `{`, `}` in arguments
            Function(arguments='\n"language": "python",\n"code": "print(\'hello world\')"', name="execute"),
        ]
        tool_calls = [
            ChatCompletionMessageToolCall(type="function", id=f"call_{i}", function=f)
            for i, f in enumerate(function_rsps)
        ]
        messages = [ChatCompletionMessage(content=None, role="assistant", tool_calls=[t]) for t in tool_calls]
        # 添加一个纯文本响应
        messages.append(
            ChatCompletionMessage(content="Completed a python code for hello world!", role="assistant", tool_calls=None)
        )
        # 添加 openai tool calls respond bug, code 出现在ChatCompletionMessage.content中
        messages.extend(
            [
                ChatCompletionMessage(content="```python\nprint('hello world')```", role="assistant", tool_calls=None),
                ChatCompletionMessage(content="'''python\nprint('hello world')'''", role="assistant", tool_calls=None),
                ChatCompletionMessage(
                    content='"""python\nprint(\'hello world\')"""', role="assistant", tool_calls=None
                ),
                ChatCompletionMessage(
                    content="'''python\nprint(\"hello world\")'''", role="assistant", tool_calls=None
                ),
                ChatCompletionMessage(content="```python\nprint('hello world')```", role="assistant", tool_calls=None),
            ]
        )
        choices = [
            Choice(finish_reason="tool_calls", logprobs=None, index=i, message=msg) for i, msg in enumerate(messages)
        ]
        return [
            ChatCompletion(id=str(i), choices=[c], created=i, model="gpt-4", object="chat.completion")
            for i, c in enumerate(choices)
        ]
