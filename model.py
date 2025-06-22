import os
import logging
from dotenv import load_dotenv

from openai import AsyncOpenAI, timeout, api_version
from agents import OpenAIChatCompletionsModel, Agent, Runner
from agents.model_settings import ModelSettings
from agents import set_default_openai_client, set_tracing_disabled
logger = logging.getLogger(__name__)

def get_model():
    # loading variables from .env file
    load_dotenv()

    # Accessing and printing value
    api_key = os.getenv("OPENAI_API_KEY")
    api_url = os.getenv("OPENAI_API_URL")
    model_name = os.getenv("OPENAI_MODEL_NAME")
    openai_temperature = os.getenv("OPENAI_TEMPERATURE")
    max_tokens = os.getenv("MAX_TOKENS")
    api_version = os.getenv("OPENAI_API_VERSION")
    query_timeout = os.getenv("OPENAI_QUERY_TIMEOUT")

    logger.info("api url is: %s", api_url)
    logger.info("api key is: %s", api_key)
    logger.info("model name is: %s", model_name)
    logger.info("openai temperature is: %s", openai_temperature)
    logger.info("max tokens is: %s", max_tokens)
    logger.info("api version is: %s", api_version)
    logger.info("query timeout is: %s", query_timeout)

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
