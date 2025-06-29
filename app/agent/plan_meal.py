import os
import logging
from agents import Agent, Runner
from agents.model_settings import ModelSettings

from app.model.model import get_model

logger = logging.getLogger(__name__)

async def plan_meal():
    model = get_model(os.getenv("OLLAMA_API_URL"), os.getenv("OLLAMA_API_KEY"), os.getenv("OLLAMA_MODEL_NAME"))

    agent = Agent(
        name="Assistant",
        instructions="You are a helpful assistant",
        model=model,
        model_settings=ModelSettings(temperature=float(os.getenv("OLLAMA_TEMPERATURE")),
                                     max_tokens=int(os.getenv("OLLAMA_MAX_TOKENS")))
    )

    result = await Runner.run(agent,
                             "Create a meal plan for a week. I'm a vegetarian. This should be for someone who wants to build muscle.")

    logger.info(result.final_output)

    return result.final_output
