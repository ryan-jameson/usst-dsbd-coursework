import openai

# 设置你的 OpenAI API 密钥
openai.api_base = "https://yunwu.ai/v1"
openai.api_key = "REDACTED_CONFIGURE_LOCALLY"

# 需要嵌入的文本
texts = [
    "Alzheimer's disease is a neurodegenerative disorder.",
    "Diabetes is a metabolic disease."
]

# 调用 embedding API
response = openai.Embedding.create(
    model="text-embedding-3-small",  # 或者 "text-embedding-ada-002"
    input=texts
)

# 提取嵌入向量
embeddings = [item['embedding'] for item in response['data']]

# 打印向量长度与示例
for i, emb in enumerate(embeddings):
    print(f"Text {i+1} embedding length: {len(emb)}")
    print(f"First 5 values: {emb[:5]}")







# ================

import openai
import time


def ask_gpt(query, streaming_flg=True, max_retries=5, flag=True):
    # - `streaming_flg`: 是否启用流式响应，默认为 True。
    # - `max_retries`: 最大重试次数，默认为 5。
    if flag:
        openai.api_base = "https://yunwu.ai/v1"
        openai.api_key = "REDACTED_CONFIGURE_LOCALLY"
    else:
        openai.api_base = "https://openkey.cloud/v1"
        openai.api_key = "REDACTED_CONFIGURE_LOCALLY"

    for attempt in range(max_retries + 1):
        try:
            start_time = time.time()
            completion = openai.ChatCompletion.create(
                #                 model="gpt-4o-mini",
                model="gpt-4o-mini",
                messages=[{'role': 'user', 'content': query}],
                stream=streaming_flg
            )
            msg = None

            if streaming_flg:
                msg, completion = process_streaming_response(completion)
            else:
                if not completion.choices:
                    raise ValueError("No choices returned from API.")
                msg = completion.choices[0].message['content']

            # 如果成功获取到消息，返回结果
            if msg:
                end_time = time.time()
#                 print(f"耗时: {end_time - start_time:.2f} 秒    GPT output: {msg}")
                time.sleep(3)
                return msg, completion

        except Exception as err:
            print(f'OpenAI API Error: {str(err)}')
            if attempt < max_retries:
                print(f"Retrying... (Attempt {attempt + 1} of {max_retries})")
                time.sleep(2 ** (attempt + 2))  # 使用指数退避策略延迟重试（延迟时间为 2^(attempt + 2) 秒）。

            else:
                if flag:
                    print("Max retries reached. Change OpenAI.")
                    return ask_gpt(query, streaming_flg, flag=False)
                else:
                    print("Max retries reached. Change OpenAI.")
                    return ask_gpt(query, streaming_flg, flag=True)


def process_streaming_response(completion):
    llist = []
    msg = ""
    for i in completion:
        if len(i['choices']) != 0:
            delta = i['choices'][0]['delta']
            content = delta.get('content', None)
            if content is not None:
                print(content, end="")
                msg += content
        else:
            continue

    def generator(llist):
        for i in llist:
            yield i

    return msg, generator(llist)


msg, _ = ask_gpt("介绍一下北京", flag=True)
print(msg)