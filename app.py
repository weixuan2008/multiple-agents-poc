import asyncio

from dotenv import load_dotenv
# loading variables from .env file
load_dotenv()

from log_config import setup_logging
# setup logging
setup_logging()

from deterministic_ollama import create_story
from search_weather import run_weather_workflow
from search_news import run_news_workflow

if __name__ == '__main__':
    # run_news_workflow("美国轰炸伊朗")
    # asyncio.run(run_weather_workflow())
    asyncio.run(create_story())

