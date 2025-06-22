import os
import logging

from openai import AsyncOpenAI, timeout, api_version
from agents import OpenAIChatCompletionsModel, Agent, Runner
from agents.model_settings import ModelSettings
from agents import set_default_openai_client, set_tracing_disabled
logger = logging.getLogger(__name__)

# Accessing and printing value
api_key = os.getenv("OPENAI_API_KEY")
api_url = os.getenv("OPENAI_API_URL")
model_name = os.getenv("OPENAI_MODEL_NAME")
openai_temperature = os.getenv("OPENAI_TEMPERATURE")
max_tokens = os.getenv("MAX_TOKENS")
api_version = os.getenv("OPENAI_API_VERSION")
query_timeout = os.getenv("OPENAI_QUERY_TIMEOUT")

logger.info(f"api url is: {api_url}...")
logger.info(f"api key is: {api_key}")
logger.info(f"model name is: {model_name}")
logger.info(f"openai temperature is: {openai_temperature}")
logger.info(f"max tokens is: {max_tokens}")
logger.info(f"api version is: {api_version}")
logger.info(f"query timeout is: {query_timeout}")

def get_model():
    external_client = AsyncOpenAI(
        base_url=api_url,
        api_key=api_key,
        # default_headers={"api-key": api_key},
        # default_query={"api-version": api_version},
        # timeout=query_timeout
    )

    model = OpenAIChatCompletionsModel(
        model=model_name,
        openai_client=external_client,
    )

    set_default_openai_client(external_client, use_for_tracing=False)
    set_tracing_disabled(disabled=True)

    return model
