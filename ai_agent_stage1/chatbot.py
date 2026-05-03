import os
from dotenv import load_dotenv
from openai import OpenAI

# 1. 加载 .env 里的密钥
load_dotenv()

# 2. 初始化客户端，把请求地址指向 DeepSeek 服务器
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# 3. 系统提示词 —— 这就是AI的“人设”，你可以随便改（后面有惊喜）
SYSTEM_PROMPT = "你是一个幽默的大学生活助手，喜欢用颜文字(。・∀・)ノ，回答简洁亲切。"

# 4. 初始化消息历史：必须包含系统设定，这是多轮对话的记忆基础
messages = [{"role": "system", "content": SYSTEM_PROMPT}]

print("===== 你的AI助手已上线！(输入 'exit' 退出，Ctrl+C 强制中断) =====")

while True:
    try:
        # 5. 获取用户输入
        user_input = input("\n你: ")
        if user_input.lower() == "exit":
            print("再见啦~")
            break

        # 6. 把用户问题也塞进历史
        messages.append({"role": "user", "content": user_input})

        # 7. 调用大模型，开启流式输出（打字机效果）
        print("AI: ", end="", flush=True)
        stream = client.chat.completions.create(
            model="deepseek-chat",      # 模型名称
            messages=messages,
            stream=True,                # 设为 True 即可逐字蹦出
            temperature=0.8             # 0.3=严谨，0.8=活泼
        )

        # 8. 拼凑完整回复，同时逐块打印
        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                full_response += content
        print()  # 打印完换一下行

        # 9. 把AI的回复也放进历史，下一轮它就能记住
        messages.append({"role": "assistant", "content": full_response})

    except KeyboardInterrupt:
        print("\n程序被强制中断。")
        break
    except Exception as e:
        print(f"\n报错啦: {e}")
        # 报错通常是因为网络或密钥，把刚才的用户输入移除，方便重试
        if messages[-1]["role"] == "user":
            messages.pop()