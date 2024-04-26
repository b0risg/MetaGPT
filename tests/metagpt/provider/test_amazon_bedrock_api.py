import pytest
import json
from metagpt.provider.bedrock.amazon_bedrock_api import AmazonBedrockLLM
from tests.metagpt.provider.mock_llm_config import mock_llm_config_bedrock
from metagpt.provider.bedrock.utils import get_max_tokens, SUPPORT_STREAM_MODELS, NOT_SUUPORT_STREAM_MODELS
from tests.metagpt.provider.req_resp_const import (
    BEDROCK_PROVIDER_REQUEST_BODY,
    BEDROCK_PROVIDER_RESPONSE_BODY,
    BEDROCK_PROVIDER_STREAM_RESPONSE)
from botocore.response import StreamingBody

# all available model from bedrock
models = SUPPORT_STREAM_MODELS | NOT_SUUPORT_STREAM_MODELS
messages = [{"role": "user", "content": "Hi!"}]


def mock_bedrock_provider_response(self, *args, **kwargs) -> dict:
    provider = self.config.model.split(".")[0]
    return BEDROCK_PROVIDER_RESPONSE_BODY[provider]


def mock_bedrock_provider_stream_response(self, *args, **kwargs) -> StreamingBody:
    provider = self.config.model.split(".")[0]
    response_json = BEDROCK_PROVIDER_STREAM_RESPONSE[provider]
    return


def get_bedrock_request_body(model_id) -> dict:
    provider = model_id.split(".")[0]
    return BEDROCK_PROVIDER_REQUEST_BODY[provider]


def is_subset(subset, superset):
    """Ensure all fields in request body are allowed.

    ```python
    subset = {"prompt": "hello","kwargs": {"temperature": 0.9,"p": 0.0}}
    superset = {"prompt": "hello", "kwargs": {"temperature": 0.0, "top-p": 0.0}}
    is_subset(subset, superset)
    ```
    >>>False
    """
    for key, value in subset.items():
        if key not in superset:
            return False
        if isinstance(value, dict):
            if not isinstance(superset[key], dict):
                return False
            if not is_subset(value, superset[key]):
                return False
    return True


@ pytest.fixture(scope="class", params=models)
def bedrock_api(request) -> AmazonBedrockLLM:
    model_id = request.param
    mock_llm_config_bedrock.model = model_id
    api = AmazonBedrockLLM(mock_llm_config_bedrock)
    return api


class TestAPI:
    def test_generate_kwargs(self, bedrock_api: AmazonBedrockLLM):
        provider = bedrock_api._get_provider()
        assert bedrock_api._generate_kwargs[provider.max_tokens_field_name] <= get_max_tokens(
            bedrock_api.config.model)

    def test_get_request_body(self, bedrock_api: AmazonBedrockLLM):
        provider = bedrock_api._get_provider()
        request_body = json.loads(provider.get_request_body(
            messages, **bedrock_api._generate_kwargs))
        print(get_bedrock_request_body(
            bedrock_api.config.model))
        print(request_body)

        assert is_subset(request_body, get_bedrock_request_body(
            bedrock_api.config.model))

    def test_completion(self, bedrock_api: AmazonBedrockLLM, mocker):
        mocker.patch(
            "metagpt.provider.bedrock.amazon_bedrock_api.AmazonBedrockLLM.invoke_model", mock_bedrock_provider_response)
        assert bedrock_api.completion(messages) == "Hello World"

    # def test_stream_completion(self, bedrock_api: AmazonBedrockLLM, mocker):
    #     mocker.patch(
    #         "metagpt.provider.bedrock.amazon_bedrock_api.AmazonBedrockLLM.invoke_model_with_response_stream", mock_bedrock_provider_response)
    #     assert bedrock_api._chat_completion_stream(messages) == "Hello World"


if __name__ == '__main__':
    print(get_bedrock_request_body("amazon.titan-tg1-large"))
