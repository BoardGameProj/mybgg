import os
from openai import AsyncOpenAI
import asyncio

client = AsyncOpenAI(
    base_url="https://api.siliconflow.cn/v1/",
    api_key=os.environ.get("OPENAI_API_KEY"),
)

async def async_translate(text):
    completion = await client.chat.completions.create(
        model="Pro/deepseek-ai/DeepSeek-V3",
        messages=[
            {
                "role": "system",
                "content": '你是一个中英文翻译专家，将用户输入的中文翻译成英文，或将用户输入的英文翻译成中文。对于非中文内容，它将提供中文翻译结果。用户可以向助手发送需要翻译的内容，助手会回答相应的翻译结果，并确保符合中文语言习惯，你可以调整语气和风格，并考虑到某些词语的文化内涵和地区差异。同时作为翻译家，需将原文翻译成具有信达雅标准的译文。"信" 即忠实于原文的内容与意图；"达" 意味着译文应通顺易懂，表达清晰；"雅" 则追求译文的文化审美和语言的优美。目标是创作出既忠于原作精神，又符合目标语言文化和读者审美的翻译。',
            },
            {
                "role": "user",
                "content": f"将以下的桌游描述文本翻译为中文，保留原始格式，不能翻译的保留原文。不要作任何解释说明：{text}",
            },
        ],
    )
    return completion.choices[0].message.content


async def async_process_queries(queries: dict):
    keys = list(queries.keys())  # 显式提取键和值
    texts = list(queries.values())
    translated_queries = await asyncio.gather(*(async_translate(text) for text in texts))
    return dict(zip(keys, translated_queries))  # 直接配对键和翻译结果