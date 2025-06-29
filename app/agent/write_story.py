import logging
import os
import re
from datetime import datetime
from pathlib import Path

from agents import Agent, Runner, function_tool, ModelSettings, trace
from pydantic import BaseModel

from app.model.model import get_model

logger = logging.getLogger(__name__)

"""
此示例演示了一个确定性流程，其中每个步骤由一个Agent执行。
1. 第一个Agent生成故事大纲
2. 我们将大纲提供给第二个Agent
3. 第二个Agent检查大纲是否质量良好，以及是否是科幻故事
4. 如果大纲质量不佳或不是科幻故事，我们就此停止
5. 如果大纲质量良好且是科幻故事，我们将大纲提供给第三个Agent
6. 第三个Agent撰写故事
7. 将最终的故事保存到本地文件
"""

# Config parameters
CONFIG = {
    "output_dir": "deterministic_output"
}

# Agent1: Create story outline
story_outline_agent = Agent(
    name="story_outline_agent",
    instructions="根据用户输入生成一个非常简短的故事大纲。",
    model=get_model(os.getenv("OLLAMA_API_URL"), os.getenv("OLLAMA_API_KEY"), os.getenv("OLLAMA_MODEL_NAME")),
    model_settings=ModelSettings(temperature=float(os.getenv("OLLAMA_TEMPERATURE")),
                                 max_tokens=int(os.getenv("OLLAMA_MAX_TOKENS"))
                                 )
)


# Define the outline to check the output structure.
# Use Pydantic model to ensure the consistency and type safety of the output format.
class OutlineChecker(BaseModel):
    good_quality: bool
    is_scifi: bool


# Agent2: Create the outline checker agent
outline_checker_agent = Agent(
    name="outline_checker_agent",
    instructions="阅读给定的故事大纲，并判断其质量。同时，确定它是否是一个科幻故事。",
    output_type=OutlineChecker,
    model=get_model(os.getenv("OLLAMA_API_URL"), os.getenv("OLLAMA_API_KEY"), os.getenv("OLLAMA_MODEL_NAME")),
    model_settings=ModelSettings(temperature=float(os.getenv("OLLAMA_TEMPERATURE")),
                                 max_tokens=int(os.getenv("OLLAMA_MAX_TOKENS"))
                                 )
)

# Agent3: Create the story writing agent
# Will write a short story based on given outline
story_agent = Agent(
    name="story_agent",
    instructions="根据给定的大纲撰写一个短篇故事。",
    output_type=str,
    model=get_model(os.getenv("OLLAMA_API_URL"), os.getenv("OLLAMA_API_KEY"), os.getenv("OLLAMA_MODEL_NAME")),
    model_settings=ModelSettings(temperature=float(os.getenv("OLLAMA_TEMPERATURE")),
                                 max_tokens=int(os.getenv("OLLAMA_MAX_TOKENS"))),
)


def remove_thinking_process(story_content):
    if "<think>" in story_content and "</think>" in story_content:
        print("检测到思考过程，正在清理...")
        # 使用正则表达式找到并移除所有<think>...</think>内容
        cleaned_text = re.sub(r'(?s)<think>.*?</think>', '', story_content)
        # 移除可能产生的多余空行
        cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
        return cleaned_text.strip()
    else:
        # 如果没有思考过程标签，返回原始文本
        return story_content


def save_story_to_file(story_content, user_prompt):
    cleaned_story = remove_thinking_process(story_content)
    save_dir = Path(CONFIG["output_dir"])
    save_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{timestamp}.txt"

    file_path = save_dir / filename

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"用户提示: {user_prompt}\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("\n==================\n\n")
        f.write(cleaned_story)

    return file_path


async def write_story():
    try:
        input_prompt = input("你想要什么类型的故事？")
        if not input_prompt.strip():
            print("提示不能为空，请重新运行程序并输入有效的提示。")
            return

        # 确保整个工作流是单个跟踪
        with trace("确定性故事流程"):
            print("正在生成故事大纲...")
            # 1. 生成大纲
            outline_result = await Runner.run(
                story_outline_agent,
                input_prompt,
            )
            print(f"已生成大纲:\n{outline_result.final_output}\n")

            # 2. 检查大纲
            print("正在检查大纲质量...")
            outline_checker_result = await Runner.run(
                outline_checker_agent,
                outline_result.final_output,
            )

            # 3. 添加一个门控，如果大纲质量不佳或不是科幻故事则停止
            assert isinstance(outline_checker_result.final_output, OutlineChecker)
            result = outline_checker_result.final_output

            if not result.good_quality:
                print("大纲质量不佳，到此为止。")
                return

            if not result.is_scifi:
                print("大纲不是科幻故事，到此为止。")
                return

            print("大纲质量良好且是科幻故事，因此我们继续撰写故事。")

            # 4. 撰写故事
            print("正在撰写故事...")
            story_result = await Runner.run(
                story_agent,
                outline_result.final_output,
            )

            # 故事初始版本
            current_story = story_result.final_output
            print(f"\n故事：\n{current_story}\n")

            # 5. 保存最终故事到本地文件
            saved_path = save_story_to_file(current_story, input_prompt)
            print(f"最终故事已保存到：{saved_path}")

    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"发生错误: {str(e)}")
