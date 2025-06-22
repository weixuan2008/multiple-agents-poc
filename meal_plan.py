import os
import logging
from agents import Agent, Runner
from agents.model_settings import ModelSettings

from model import get_model

logger = logging.getLogger(__name__)


def meal_plan():
    model = get_model()

    agent = Agent(
        name="Assistant",
        instructions="You are a helpful assistant",
        model=model,
        model_settings=ModelSettings(temperature=float(os.getenv("OPENAI_TEMPERATURE")),
                                     max_tokens=int(os.getenv("MAX_TOKENS")))
    )

    result = Runner.run_sync(agent,
                             "Create a meal plan for a week. I'm a vegetarian. This should be for someone who wants to build muscle.")
    logger.info(result.final_output)
