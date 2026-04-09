import os
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
def get_deepseek_llm(temperature: float = 0.2) -> ChatOpenAI:
    """
    初始化并返回 DeepSeek 大模型实例。
    注意事项：
    1. 金融场景对事实要求高，默认 temperature 设为较低的 0.2 以降低幻觉。
    2. DeepSeek API 兼容 OpenAI 格式，因此直接复用 ChatOpenAI 类。
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("DEEPSEEK_BASE_URL")

    if not api_key:
        raise ValueError("未找到 DEEPSEEK_API_KEY，请检查 .env 文件配置！")

    # 使用 deepseek-chat (V3模型)，性价比最高，适合做基础的写作和核查
    llm = ChatOpenAI(
        model="deepseek-chat",
        api_key=api_key,
        base_url=base_url,
        temperature=temperature,
        max_tokens=2048
    )
    return llm


# 简单测试代码（直接运行此文件时触发）
if __name__ == "__main__":
    llm = get_deepseek_llm()
    response = llm.invoke("请用一句话解释什么是市盈率(PE)？")
    print(f"DeepSeek 测试连接成功: {response.content}")