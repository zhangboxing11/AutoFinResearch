import gradio as gr
from src.main import build_workflow

print("正在初始化 Agent 引擎...")
agent_app = build_workflow()


def run_research(topic):
    """前端传入 topic，后端返回研报"""
    initial_state = {
        "topic": topic,
        "revision_count": 0,
        "is_valid": False
    }
    final_state = agent_app.invoke(initial_state)
    return final_state["report_draft"]


# ==========================================
# 进阶美化版 UI 设计 (使用 Blocks 架构)
# ==========================================

# 1. 注入一点极简的 CSS 来隐藏不需要的元素，增加圆角
custom_css = """
footer {display: none !important;} /* 强制隐藏网页底部的 Gradio 水印 */
.textbox-container textarea {font-size: 15px !important;} /* 输入框字体稍微调大 */
"""

# 2. 使用 Soft 主题，主色调设为科技蓝 (slate)
with gr.Blocks(title="AutoFinResearch") as demo:
    # 顶部标题区
    gr.Markdown(
        """
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="font-weight: 800; color: #1e293b;">📈 AutoFinResearch 深度投研智能体</h1>
            <p style="font-size: 16px; color: #64748b;">V2.0 架构：多智能体 Plan-and-Solve | 真实全网检索 | 事实交叉核查</p>
        </div>
        """
    )

    # 主体布局区：左边输入，右边输出 (1:2的比例)
    with gr.Row():
        # 左侧控制面板
        with gr.Column(scale=1):
            topic_input = gr.Textbox(
                lines=4,
                placeholder="在此输入宏观研究主题，例如：\n\n特斯拉 2025 年 FSD 自动驾驶的盈利预测及核心风险提示...",
                label="🔍 设定研究方向"
            )
            submit_btn = gr.Button("🚀 启动深度研究引擎", variant="primary", size="lg")

            gr.Markdown(
                """
                **💡 执行流程：**
                1. 🧠 **规划师**拆解研究子课题
                2. 🌐 **研究员**全网检索最新事实
                3. ✍️ **主笔**汇总资料撰写长文
                4. ⚖️ **审核员**交叉比对防止幻觉
                """
            )

        # 右侧结果展示面板
        with gr.Column(scale=2):
            # 将 markdown 放在一个带边框的 Group 里显得更规整
            with gr.Group():
                output_markdown = gr.Markdown(
                    value="*等待指令输入中... 喝口水，这通常需要 1-2 分钟的思考与全网检索时间。*",
                    label="📄 深度研究报告"
                )

    # 绑定点击事件：点击按钮后，拿左边的输入去运行函数，结果渲染到右边
    submit_btn.click(
        fn=run_research,
        inputs=topic_input,
        outputs=output_markdown
    )

if __name__ == "__main__":
    # 启动网页服务，将主题和自定义 CSS 放在启动环节注入
    demo.launch(theme=gr.themes.Soft(primary_hue="slate"), css=custom_css)