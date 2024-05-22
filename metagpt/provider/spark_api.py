#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sparkai.core.messages import _convert_to_message, convert_to_messages
from sparkai.llm.llm import ChatSparkLLM

from metagpt.configs.llm_config import LLMConfig, LLMType
from metagpt.const import USE_CONFIG_TIMEOUT
from metagpt.logs import log_llm_stream
from metagpt.provider.base_llm import BaseLLM
from metagpt.provider.llm_provider_registry import register_provider

# from sparkai.schema import LLMResult, HumanMessage, AIMessage 由于其使用Pydantic V1,导入会报错


@register_provider(LLMType.SPARK)
class SparkLLM(BaseLLM):
    """
    用于讯飞星火大模型系列
    参考：https://github.com/iflytek/spark-ai-python"""

    def __init__(self, config: LLMConfig):
        self.config = config
        self._init_client()

    def _init_client(self):
        self.client = ChatSparkLLM(
            spark_api_url=self.config.base_url,
            spark_app_id=self.config.app_id,
            spark_api_key=self.config.api_key,
            spark_api_secret=self.config.api_secret,
            spark_llm_domain=self.config.domain,
            streaming=True,
        )

    def _system_msg(self, msg: str):
        return _convert_to_message(msg)

    def _user_msg(self, msg: str, **kwargs):
        return _convert_to_message(msg)

    def _assistant_msg(self, msg: str):
        return _convert_to_message(msg)

    def get_choice_text(self, rsp) -> str:
        return rsp.generations[0][0].text

    def get_usage(self, response):
        message = response.generations[0][0].message
        if hasattr(message, "additional_kwargs"):
            return message.additional_kwargs.get("token_usage", {})
        else:
            return {}

    async def _achat_completion(self, messages: list[dict], timeout=USE_CONFIG_TIMEOUT):
        messages = convert_to_messages(messages)
        response = await self.client.agenerate([messages])
        usage = self.get_usage(response)
        self._update_costs(usage)
        return response

    async def acompletion(self, messages: list[dict], timeout=USE_CONFIG_TIMEOUT):
        return self._achat_completion(messages, timeout)

    async def _achat_completion_stream(self, messages: list[dict], timeout: int = USE_CONFIG_TIMEOUT) -> str:
        response = self.client.astream(messages)
        collected_content = []
        usage = {}
        async for chunk in response:
            collected_content.append(chunk.content)
            log_llm_stream(chunk.content)
            if hasattr(chunk, "additional_kwargs"):
                usage = chunk.additional_kwargs.get("token_usage", {})

        log_llm_stream("\n")
        self._update_costs(usage)
        full_content = "".join(collected_content)
        return full_content
