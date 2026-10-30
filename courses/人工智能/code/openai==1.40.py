# conda activate graphrag

## embedding模型

from openai import OpenAI

client = OpenAI(
    base_url = "https://yunwu.ai/v1",
    api_key="REDACTED_CONFIGURE_LOCALLY"
)

# 需要嵌入的文本
texts = [
    "Alzheimer's disease is a neurodegenerative disorder.",
    "Diabetes is a metabolic disease."
]

# 调用 embedding API
response = client.embeddings.create(
    model="text-embedding-3-small",  # 或者 "text-embedding-ada-002"
    input=texts
)

# 提取嵌入向量
embeddings = [item.embedding for item in response.data]

# 打印向量长度与示例
for i, emb in enumerate(embeddings):
    print(f"Text {i+1} embedding length: {len(emb)}")
    print(f"First 5 values: {emb[:5]}")







# ==============

import time
from openai import OpenAI
from openai.types.chat import ChatCompletionChunk

# 全局客户端缓存
client = None


def ask_gpt(query, streaming_flg=True, max_retries=5, flag=True):
    """
    发起 GPT 请求
    - streaming_flg: 是否启用流式响应
    - max_retries: 最大重试次数
    - flag: 用于切换 base_url 和 key
    """
    global client

    # 根据 flag 选择 API base 和 key
    if flag:
        api_base = "https://yunwu.ai/v1" 
        api_key = "REDACTED_CONFIGURE_LOCALLY"
    else:
        api_base = "https://openkey.cloud/v1"
        api_key = "REDACTED_CONFIGURE_LOCALLY"

    client = OpenAI(api_key=api_key, base_url=api_base)

    for attempt in range(max_retries + 1):
        try:
            start_time = time.time()

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": query}],
                stream=streaming_flg,
            )

            msg = None

            if streaming_flg:
                msg, response = process_streaming_response(response)
            else:
                if not response.choices:
                    raise ValueError("No choices returned from API.")
                msg = response.choices[0].message.content

            if msg:
                end_time = time.time()
                time.sleep(3)
                return msg, response

        except Exception as err:
            print(f"OpenAI API Error: {str(err)}")
            if attempt < max_retries:
                print(f"Retrying... (Attempt {attempt + 1} of {max_retries})")
                time.sleep(2 ** (attempt + 2))
            else:
                print("Max retries reached. Switching OpenAI endpoint.")
                return ask_gpt(query, streaming_flg, flag=not flag)


def process_streaming_response(response: ChatCompletionChunk):
    msg = ""
    for chunk in response:
        if chunk.choices:
            delta = chunk.choices[0].delta
            content = delta.content if delta and delta.content else ""
            print(content, end="", flush=True)
            msg += content

    return msg, response


# 示例调用
msg, _ = ask_gpt("介绍一下北京")