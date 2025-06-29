"""
案例展示了交接/路由模式。分流代理接收第一条消息，
然后根据请求的语言将其交给适当的代理，响应会实时流式传输给用户。
"""
import logging
import os

from agents import OpenAIChatCompletionsModel, Agent, ModelSettings, TResponseInputItem, Runner, RawResponsesStreamEvent
from openai.types.responses import ResponseTextDeltaEvent, ResponseContentPartDoneEvent

from app.model.model import get_model

logger = logging.getLogger(__name__)


class OllamaOpenAIChatCompletionsModel(OpenAIChatCompletionsModel):
    """适配器模式实现: 处理Ollama API的响应格式与OpenAI API的差异"""

    # 采用异步方式处理流式响应，确保模型生成的文本可以实时地逐部分返回给用户。
    async def stream_raw_text(self, *argc, **kwargs):
        """ 重写流处理方法
            确保了所有模型（无论是OpenAI还是Ollama）都遵循相同的接口
        """
        # 调用父类的方法进行流式处理
        async for event in await super().stream_raw_text(*args, **kwargs):
            # 将每个事件逐个传递给调用者
            # 使得模型生成的文本能够实时地流式传输给用户，而不是等待整个响应完成。
            yield event


# 代理1: 法语代理
french_agent = Agent(
    name="french_agent",
    instructions="你只说法语",
    model=get_model(os.getenv("OLLAMA_API_URL"), os.getenv("OLLAMA_API_KEY"), os.getenv("OLLAMA_MODEL_NAME")),
    model_settings=ModelSettings(temperature=float(os.getenv("OLLAMA_TEMPERATURE")),
                                 max_tokens=int(os.getenv("OLLAMA_MAX_TOKENS")))
)

# 代理2: 中文代理
chinese_agent = Agent(
    name="chinese_agent",
    instructions="你只说中文",
    model=get_model(os.getenv("OLLAMA_API_URL"), os.getenv("OLLAMA_API_KEY"), os.getenv("OLLAMA_MODEL_NAME")),
    model_settings=ModelSettings(temperature=float(os.getenv("OLLAMA_TEMPERATURE")),
                                 max_tokens=int(os.getenv("OLLAMA_MAX_TOKENS")))
)

# 代理3: 英语代理
english_agent = Agent(
    name="english_agent",
    instructions="你只说英语",
    model=get_model(os.getenv("OLLAMA_API_URL"), os.getenv("OLLAMA_API_KEY"), os.getenv("OLLAMA_MODEL_NAME")),
    model_settings=ModelSettings(temperature=float(os.getenv("OLLAMA_TEMPERATURE")),
                                 max_tokens=int(os.getenv("OLLAMA_MAX_TOKENS")))
)

# 代理4: 分流代理 - 负责判断用户使用的语言并将请求路由到对应的语言代理
router_agent = Agent(
    name="router_agent",
    instructions="根据请求的语言将其交给适当的代理。",
    handoffs=[french_agent, chinese_agent, english_agent],
    model=get_model(os.getenv("OLLAMA_API_URL"), os.getenv("OLLAMA_API_KEY"), os.getenv("OLLAMA_MODEL_NAME")),
    model_settings=ModelSettings(temperature=float(os.getenv("OLLAMA_TEMPERATURE")),
                                 max_tokens=int(os.getenv("OLLAMA_MAX_TOKENS")))
)


async def translate_language():
    try:
        msg = input("你好！我们会说法语、中文和英语。我能帮你什么忙？ ")
        # 初始化代理为分流代理
        agent = router_agent
        # 创建输入列表，包含用户的第一条消息（用于保存完整的对话历史）
        inputs: list[TResponseInputItem] = [{"content": msg, "role": "user"}]
        # 无限循环，持续处理用户的输入和代理的响应
        while True:
            # 运行当前代理
            result = Runner.run_streamed(
                agent,
                input=inputs,
            )

            # 异步遍历流式事件
            async for event in result.stream_events():
                # 过滤出原始响应流事件
                # 流式响应系统中会产生多种类型的事件，例如：原始响应事件（包含实际文本内容），
                # 元数据事件（处理状态、连接信息等，系统控制事件（开始、结束、错误等）
                if not isinstance(event, RawResponsesStreamEvent):
                    continue
                # 模型生成的实际内容数据，主要有两种类型。
                # 1. 文本增量事件（ResponseTextDeltaEvent）：包含实际的文本内容。
                # 2. 内容部分完成事件（ResponseContentPartDoneEvent）：表示一个完整的响应块已经生成。
                data = event.data
                # 判断事件数据类型
                # 如果是文本增量，立即打印文本片段，不换行。
                if isinstance(data, ResponseTextDeltaEvent):
                    #  data.delta属性获取具体的文本片段
                    print(data.delta, end="", flush=True)
                # 如果是内容部分完成，打印换行符。
                elif isinstance(data, ResponseContentPartDoneEvent):
                    print("\n")

            # 获取更新后的对话历史
            inputs = result.to_input_list()
            logger.info("\n")

            # 获取用户的下一条消息
            user_msg = input("Enter a message: ")
            # 将用户消息添加到输入列表
            inputs.append({"content": user_msg, "role": "user"})
            # 更新当前代理为结果中的代理（已经由分流代理交接给了语言代理）
            agent = result.current_agent

    # 异常处理
    except KeyboardInterrupt:
        # 处理用户中断（Ctrl+C）
        print("\n程序被用户中断")
    except Exception as e:
        # 处理其他异常
        print(f"发生错误: {str(e)}")
