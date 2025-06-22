import os
import logging
from dotenv import load_dotenv


from meal_plan import meal_plan
from search_news import run_news_workflow

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # loading variables from .env file
    load_dotenv()

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', filename="./logs/basic_agent.log",
                        level=logging.INFO)
    # meal_plan()
    run_news_workflow("openai agent sdk")
