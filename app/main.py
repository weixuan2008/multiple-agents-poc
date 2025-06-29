import asyncio

from dotenv import load_dotenv
load_dotenv()
from log_config import setup_logging
setup_logging()

# from app.agent.write_story import write_story
# from app.agent.search_news import search_news
# from app.agent.search_weather import search_weather
# from app.agent.plan_meal import plan_meal
from app.agent.translate_language import translate_language

if __name__ == '__main__':
    # asyncio.run(plan_meal())
    # asyncio.run(search_news("美国轰炸伊朗"))
    # asyncio.run(search_weather("北京"))
    # asyncio.run(write_story())
    asyncio.run(translate_language())
