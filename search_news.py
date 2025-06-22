import os
import logging
from datetime import datetime

from agents import Agent, Runner, function_tool
from agents.model_settings import ModelSettings
from duckduckgo_search import DDGS

from model import get_model

logger = logging.getLogger(__name__)
current_date = datetime.now().strftime("%Y-%m")


# 1. Create internet search tool
@function_tool
def get_news_articles(topic):
    logger.info(f"Running DuckDuckGo news search for {topic}...")

    # DuckDuckGo search
    ddg_api = DDGS()
    results = ddg_api.text(f"{topic} {current_date}", max_results=5)

    if results:
        news_results = "\n\n".join(
            [f"Title: {result['title']}\nURL: {result['href']}\nDescription: {result['body']}" for result in results])
        logger.info(news_results)
        return news_results
    else:
        return f"Could not find news results for {topic}."


# 2. Create AI agents
# News agent to fetch news
news_agent = Agent(
    name="News Assistant",
    instructions="You provide the latest news articles for a given topic using DuckDuckGo search.",
    tools=[get_news_articles],
    model=get_model(),
    model_settings=ModelSettings(temperature=float(os.getenv("OPENAI_TEMPERATURE")),
                                 max_tokens=int(os.getenv("MAX_TOKENS")))
)

# Editor agent to edit news
editor_agent = Agent(
    name="Editor Assistant",
    instructions="Rewrite and give me as news article ready for publishing. Each News story in separate section.",
    model=get_model(),
    model_settings=ModelSettings(temperature=float(os.getenv("OPENAI_TEMPERATURE")),
                                 max_tokens=int(os.getenv("MAX_TOKENS")))
)


# 3. Create wokflow
def run_news_workflow(topic):
    logger.info("Running news Agent workflow...")

    # Step1, fetch news
    news_response = Runner.run_sync(news_agent, f"Get me the news about {topic} on {current_date}")

    # Access the content from RunResult object
    raw_news = news_response.final_output

    # Step2, pass news to editor for final review
    edited_news_response = Runner.run_sync(editor_agent, raw_news)

    # Access the content from RunResult object
    edited_news = edited_news_response.final_output

    logger.info("Final news articles:")
    logger.info(edited_news)
    return edited_news
