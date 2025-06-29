import os
import logging

from openai import AsyncOpenAI, timeout, api_version
from agents import OpenAIChatCompletionsModel, Agent, Runner
from agents.model_settings import ModelSettings
from agents import set_default_openai_client, set_tracing_disabled
logger = logging.getLogger(__name__)

def get_model(api_url, api_key, model_name):
    logger.info(f"The api url is {api_url}.")
    logger.info(f"The api key is {api_key}.")
    logger.info(f"The model name is {model_name}.")

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
