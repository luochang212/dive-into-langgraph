# -*- coding: utf-8 -*-

"""
Gradio 聊天界面

定义聊天界面样式，通过 `generate_response` 函数模拟大语言模型的回复。
"""

import gradio as gr
import random
import time
import os


# 模拟大语言模型生成回复
def generate_response(message, history):
    if not message.strip():
        return message, history

    # 模拟大语言模型处理延迟
    processing_time = random.uniform(0.5, 1.5)
    time.sleep(processing_time)

    # 模拟生成智能回复
    responses = [
        "这是一个基于大语言模型的回复示例。",
        "我理解你的查询了。",
        "感谢你的提问！"
    ]

    # 使用新的消息格式
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": random.choice(responses)})
    return "", history


# 自定义 CSS 样式
custom_css = """
@font-face {
    font-family: 'Source Han Sans CN';
    src: url('https://s2.loli.net/2024/06/10/3YNvDwcS7kK9P1E.woff2')  format('woff2');
}

html, body {
    height: 100%;
    margin: 0;
    overflow: hidden;
}

:root {
    --primary: #007AFF;
    --secondary: #0066CC;
    --dark: #1C1C1E;
    --light: #F2F2F7;
    --gray: #E5E5EA;
}

/* 全局样式覆盖 */
.gradio-container {
    background: #181818 !important;
}

.dark .gradio-container {
    padding: 0;
    margin: 0;
    height: 100vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

/* 标题栏固定高度 */
#header {
    flex: 0 0 auto;
    height: 60px !important;
    overflow: hidden;
    margin: 0 !important;
    padding: 10px 0 !important;
    background: #181818;
    z-index: 10;
}

#header h1 {
    margin: 0 !important;
    padding: 0 !important;
    font-size: 24px !important;
    line-height: 40px !important;
}

/* 聊天区域样式 */
#chatbot {
    flex: 1 1 auto;
    height: calc(100vh - 60px) !important; /* 减去固定的标题栏高度 */
    overflow-y: auto !important;
    padding-bottom: 160px !important;
    box-sizing: border-box !important;
    background-color: #181818 !important;
    margin-top: 0 !important;
    display: flex !important;
    flex-direction: column !important;

    /* Firefox 滚动条样式 */
    scrollbar-width: thin !important;
    scrollbar-color: rgba(255, 255, 255, 0.1) transparent !important;
}

/* Webkit 浏览器(Chrome/Safari)滚动条样式 */
#chatbot::-webkit-scrollbar {
    width: 6px !important;
    height: 6px !important;
}

#chatbot::-webkit-scrollbar-track {
    background: transparent !important;
}

#chatbot::-webkit-scrollbar-thumb {
    background-color: rgba(255, 255, 255, 0.1) !important;
    border-radius: 3px !important;
}

#chatbot::-webkit-scrollbar-thumb:hover {
    background-color: rgba(255, 255, 255, 0.2) !important;
}

#chatbot > .wrapper {
    display: flex !important;
    flex-direction: column !important;
    flex-grow: 1 !important;
}

/* 强制覆盖 Chatbot 内部容器背景 */
#chatbot > .wrapper, 
#chatbot .bubble-wrap {
    background-color: #181818 !important;
}

/* 确保消息列表背景透明或匹配 */
#chatbot .message-wrap {
    background-color: #181818 !important;
}

/* 确保消息行占满宽度并处理边距 */
/* AI 回复头像及文字气泡 */
#chatbot .bot-row {
    margin-left: 15% !important; /* AI 消息向右移动 */
    width: 75% !important;
}

/* 用户回复头像及文字气泡 */
#chatbot .user-row {
    margin-right: 15% !important; /* 用户消息向左移动 */
    max-width: 40% !important;
    # width: 80% !important;
}

/* AI 回复气泡透明无边框 - 多版本兼容选择器 */
.bot.message {
    width: 83% !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding-left: 0 !important;
}

/* 输入区域样式 */
.input-row {
    position: fixed !important;
    bottom: 30px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 1000;
    width: 90%;
    height: auto;
    max-width: 800px;
    display: flex;
    flex-direction: row !important; /* 强制水平排列 */
    flex-wrap: nowrap !important;   /* 强制不换行 */
    justify-content: center !important;
    align-items: center !important; /* 恢复居中对齐，保持原有位置关系 */
    margin: 0 !important;
    gap: 12px;
    padding: 20px;
    background: #1e1e1e !important; /* 稍微提亮背景色 */
    border-radius: 30px; /* 增加圆角，使其更像悬浮岛 */
    box-shadow: 
        0 20px 50px rgba(0,0,0,0.5),       /* 深色投影增加悬浮感 */
        0 0 0 1px rgba(255,255,255,0.1),   /* 细微的亮边框 */
        0 0 20px rgba(255,255,255,0.05);   /* 柔和的外发光 */
    border: 1px solid rgba(255,255,255,0.1);
    backdrop-filter: blur(20px); /* 毛玻璃效果 */
}

/* 文本框样式 */
.textbox {
    flex: 1 1 auto;
    border-radius: 24px;
    padding: 0 !important; /* Gradio 内部 padding */
    background: var(--dark);
    color: var(--dark);
    font-size: 16px;
    box-shadow: none !important; /* 移除输入框自身的阴影，统一由容器管理 */
    transition: all 0.3s ease !important;
    border: 1px solid rgba(255,255,255,0.1);
}

.textbox textarea {
    height: 80px !important;
    overflow-y: auto;
    resize: none;
    width: 100%;
    display: block;
    line-height: 1.5;
    scrollbar-width: none;  /* Firefox */
}

/* 隐藏滚动条但保留滚动功能 */
.textbox textarea::-webkit-scrollbar {
    display: none;
}

/* 焦点效果 */
.textbox:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.2) !important;
}

/* 按钮样式 */
.button {
    flex: 0 0 auto;
    height: 45px;
    min-width: 80px;
    padding: 0 20px;
    border-radius: 24px !important;
    background: var(--primary) !important;
    color: white !important;
    border: none !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 12px rgba(0, 122, 255, 0.2) !important;
}

/* 悬停效果 */
.button:hover {
    background: var(--secondary) !important;
    box-shadow: 0 6px 16px rgba(0, 122, 255, 0.3) !important;
}

/* 点击效果 */
.button:active {
    transform: scale(0.98);
}

.dark, .textbox, .user, .assistant {
    font-family: "Microsoft YaHei", "PingFang SC", "Ali普惠体", sans-serif;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
    /* 移动端恢复默认边距 */
    #chatbot .bot-row {
        margin-left: 50px !important;
        width: calc(100% - 50px) !important;
    }

    #chatbot .user-row {
        margin-right: 50px !important;
        width: calc(100% - 50px) !important;
        margin-left: auto !important;
    }

    .textbox {
        padding: 10px 16px !important;
        font-size: 14px !important;
    }

    .button {
        min-width: 60px;
        padding: 0 12px;
        font-size: 14px;
    }
}

/* Tool Result 样式 */
.tool-result-summary::-webkit-details-marker { display: none; }
.tool-result-summary { list-style: none; display: flex; justify-content: space-between; align-items: center; cursor: pointer; font-weight: bold; color: #eee; outline: none; }
.tool-result-details[open] .tool-result-icon { transform: rotate(180deg); }
.tool-result-icon { transition: transform 0.2s ease; }

/* 隐藏 Chatbot 右上角的清空/删除按钮 */
#chatbot button[aria-label="Clear"] {
    display: none !important;
}
"""


# 主题配置
theme = gr.themes.Soft(primary_hue="blue", secondary_hue="blue")


def create_ui(llm_func, tab_name, main_title, initial_message=None):
    """创建聊天界面"""
    with gr.Blocks(title=tab_name, fill_width=True) as ui:
        # 标题区域
        gr.Markdown(
            f"""
            # <center>{main_title}</center>
            """,
            elem_id="header",  # 添加 ID 以便 CSS 精确定位
            elem_classes=["dark"]
        )

        # 头像路径
        root_dir = os.path.dirname(os.path.dirname(__file__))
        user_avatar_path = os.path.join(root_dir, "images", "user.png")
        ai_avatar_path = os.path.join(root_dir, "images", "ai.png")

        # 聊天区域
        chatbot = gr.Chatbot(
            value=initial_message,
            elem_id="chatbot",
            avatar_images=(
                user_avatar_path,  # 用户头像
                ai_avatar_path     # AI头像
            ),
            height=600,
            show_label=False,
            elem_classes=["dark"],
            buttons=[]  # 禁用右上角的所有按钮（分享、复制、清空等）
        )

        # 输入区域
        with gr.Row(elem_classes=["input-row", "dark"]) as input_row:
            msg = gr.Textbox(
                placeholder="输入消息...",
                show_label=False,
                container=False,
                elem_classes=["textbox", "dark"]
            )
            submit_btn = gr.Button("发送", elem_classes=["button"])

        msg.submit(
            llm_func,
            [msg, chatbot],
            [msg, chatbot]
        )
        
        submit_btn.click(
            llm_func,
            [msg, chatbot],
            [msg, chatbot]
        )
    
    return ui


if __name__ == "__main__":
    app = create_ui(
        llm_func=generate_response,
        tab_name="Gradio APP - WebUI",
        main_title="Gradio WebUI Demo",
    )

    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,  # 内部使用时，必须为 False
        theme=theme,
        css=custom_css
    )
